import streamlit as st
import whisper  
import os
import tempfile
from db import get_db_conn
from datetime import datetime
from llm import get_qa_response
import base64
import pdfkit
from admin import render_upload_pdf, render_manage_pdfs  

@st.cache_resource 
def load_whisper_model():
    """Load and cache Whisper model"""
    try:
        model = whisper.load_model("base")  
        return model
    except Exception as e:
        st.error(f"Failed to load Whisper model: {e}. Voice feature disabled. Install with 'pip install openai-whisper' and ensure ffmpeg is in PATH.")
        return None

def transcribe_audio(audio_bytes):
    """Transcribe audio bytes to text using Whisper"""
    model = load_whisper_model()
    if not model:
        return "Whisper not available. Please check installation."
    try:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes.getvalue())
            tmp_path = tmp_file.name
       
        result = model.transcribe(tmp_path, language="en")  
        os.unlink(tmp_path) 
        transcribed = result["text"].strip()
        if transcribed:
            return transcribed
        else:
            return "No speech detected. Try speaking louder or closer to the mic."
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""

def render_chat(user_id):
    
    st.sidebar.subheader("🔍 Quick Search History")
    search_query = st.sidebar.text_input("Search questions or answers", placeholder="Type to search...")
    if search_query:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("""SELECT id, question, answer, created_at
                       FROM history WHERE user_id=? AND (question LIKE ? OR answer LIKE ?)
                       ORDER BY created_at DESC LIMIT 5""", (user_id, f"%{search_query}%", f"%{search_query}%"))
        results = cur.fetchall()
        conn.close()
        with st.sidebar.expander(f"📋 {len(results)} Results", expanded=True):
            for r in results:
                with st.container():
                    st.markdown(f"**{r['created_at'][:16]}**")
                    st.markdown(f"**Q:** {r['question'][:80]}...")
                    st.markdown(f"**A:** {r['answer'][:100]}...")
                    st.markdown("---")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Navigation")
    st.sidebar.info("Use the selectbox above to switch pages.")
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                meta = message.get("meta", {})
                bookmarked = meta.get("bookmarked", False)
                col1, col2 = st.columns([0.98, 0.02])
                with col2:
                    
                    btn_emoji = "⭐" if bookmarked else "★"
                    btn_color = "gold" if bookmarked else "gray"
                    if st.button(btn_emoji, key=f"bm_chat_{i}", help="Toggle Bookmark", use_container_width=False):
                        if not bookmarked:
                            history_id = meta.get("history_id")
                            if history_id:
                                conn = get_db_conn()
                                cur = conn.cursor()
                                cur.execute("UPDATE history SET is_bookmark=1 WHERE id=?", (history_id,))
                                conn.commit()
                                conn.close()
                                message["meta"]["bookmarked"] = True
                                st.rerun()
    
    st.markdown("---")
    st.subheader("💭 Ask a question")
    user_q = st.text_area("Your question (or record voice below)", height=120, key="user_q", placeholder="Type your question here or use voice input...")
    col_voice, col_submit = st.columns([1, 1])
    with col_voice:
       
        audio = st.audio_input("🎤 Record Voice Message (tap to start speaking)")
        if audio:
            with st.spinner("Transcribing voice..."):
                transcribed_text = transcribe_audio(audio)
                user_q = transcribed_text  
                st.success(f"✅ Transcribed: '{transcribed_text}'")
                st.audio(audio)  
    with col_submit:
        submit = st.button("🚀 Send", use_container_width=True)
    if submit and user_q.strip():
        
        st.session_state.messages.append({"role": "user", "content": user_q})
        vectorstore_path = "vectorstore/db_faiss"
        if not os.path.exists(vectorstore_path):
            st.error("📚 Knowledge base not ready. Upload PDFs first.")
        else:
            with st.chat_message("user"):
                st.markdown(user_q)
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    answer = get_qa_response(user_q)  
                 
                    ass_msg = {
                        "role": "assistant",
                        "content": answer,
                        "meta": {"bookmarked": False},
                        "question": user_q
                    }
                    st.session_state.messages.append(ass_msg)
                    st.markdown(answer)
                    
                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO history (user_id, question, answer, is_bookmark, created_at) VALUES (?, ?, ?, 0, ?)",
                                (user_id, user_q, answer, datetime.now().isoformat()))
                    history_id = cur.lastrowid
                    conn.commit()
                    ass_msg["meta"]["history_id"] = history_id
                    conn.close()
        st.rerun()
   
    st.markdown("---")
    st.subheader("📤 Export Current Chat")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📄 Generate PDF", use_container_width=True):
            def render_chat_html(messages):
                html = ["<html><head><meta charset='utf-8'><style>body{font-family:Arial;padding:20px;} .u{background:#e6f0ff;padding:10px;border-radius:6px;margin:8px 0;} .b{background:#f2f2f2;padding:10px;border-radius:6px;margin:8px 0;}</style></head><body>"]
                html.append(f"<h2>MITBot Chat Export - {st.session_state.user['username']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>")
                for m in messages:
                    if m["role"] == "user":
                        html.append(f"<div class='u'><b>You:</b> {m['content']}</div>")
                    else:
                        html.append(f"<div class='b'><b>MITBot:</b> {m['content']}</div>")
                html.append("</body></html>")
                return "\n".join(html)
            if not st.session_state.messages:
                st.warning("No chat to export.")
            else:
                html = render_chat_html(st.session_state.messages)
                try:
                    pdf_name = f"mitbot_chat_{int(datetime.now().timestamp())}.pdf"
                    pdfkit.from_string(html, pdf_name)
                    with open(pdf_name, "rb") as f:
                        st.download_button("⬇️ Download Chat PDF", f, file_name=f"mitbot_{st.session_state.user['username']}_chat.pdf", mime="application/pdf", use_container_width=True)
                    os.remove(pdf_name)
                except Exception as e:
                    st.error("PDF generation failed: " + str(e))
                    st.info("Ensure wkhtmltopdf installed and accessible.")

def render_history(user_id):
    st.header("📚 My Chat History")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""SELECT id, question, answer, created_at, is_bookmark
                   FROM history WHERE user_id=? ORDER BY created_at DESC""", (user_id,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        st.info("📭 No history yet. Start chatting to build your history!")
    else:
        
        selected_ids = st.multiselect("Select entries to delete:", [r["id"] for r in rows], key="multi_delete")
        if st.button("🗑️ Delete Selected"):
            if selected_ids:
                conn = get_db_conn()
                cur = conn.cursor()
                for sid in selected_ids:
                    cur.execute("DELETE FROM history WHERE id=?", (sid,))
                conn.commit()
                conn.close()
                st.success(f"Deleted {len(selected_ids)} entries.")
                st.rerun()
        for r in rows:
            bookmark_emoji = "⭐ " if r['is_bookmark'] else "★ "
            with st.expander(f"{bookmark_emoji} {r['created_at'][:16]}"):
                st.markdown(f"**Q:** {r['question']}")
                st.markdown(f"**A:** {r['answer']}")
                col1, col2 = st.columns([0.95, 0.05])
                with col2:
                    
                    if st.button("🗑️", key=f"del_hist_{r['id']}"):
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM history WHERE id=?", (r['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
                    
                    if r['is_bookmark'] == 0:
                        if st.button("⭐ Bookmark", key=f"bm_hist_{r['id']}"):
                            conn = get_db_conn()
                            cur = conn.cursor()
                            cur.execute("UPDATE history SET is_bookmark=1 WHERE id=?", (r['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()

def render_bookmarks(user_id):
    st.header("⭐ My Bookmarks")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""SELECT id, question, answer, created_at
                   FROM history WHERE user_id=? AND is_bookmark=1 ORDER BY created_at DESC""", (user_id,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        st.info("📭 No bookmarks yet. Bookmark responses in chat to save them here!")
    else:
        
        selected_ids = st.multiselect("Select bookmarks to remove:", [r["id"] for r in rows], key="multi_rm_bm")
        if st.button("❌ Remove Selected"):
            if selected_ids:
                conn = get_db_conn()
                cur = conn.cursor()
                for sid in selected_ids:
                    cur.execute("UPDATE history SET is_bookmark=0 WHERE id=?", (sid,))
                conn.commit()
                conn.close()
                st.success(f"Removed {len(selected_ids)} bookmarks.")
                st.rerun()
        for r in rows:
            with st.expander(f"⭐ {r['created_at'][:16]}"):
                st.markdown(f"**Q:** {r['question']}")
                st.markdown(f"**A:** {r['answer']}")
                col1, col2 = st.columns([0.95, 0.05])
                with col2:
                    if st.button("❌ Remove", key=f"rm_bm_{r['id']}"):
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("UPDATE history SET is_bookmark=0 WHERE id=?", (r['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

def render_user_uploads(user_id):
    st.header("📤 My PDF Uploads")
    render_upload_pdf(user_id)  
    st.markdown("---")
    render_manage_pdfs(user_id)  