import streamlit as st
import os
import base64
from datetime import datetime
from db import get_db_conn
from vectorstore import build_faiss_from_pdfs
from settings import get_settings, set_settings

DATA_DIR = "data"  

def render_dashboard():
    st.header("📊 Admin Dashboard")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM users")
    users_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM pdfs")
    pdf_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM history")
    hist_count = cur.fetchone()["c"]
    conn.close()
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Users", users_count)
    col2.metric("📄 Uploaded PDFs", pdf_count)
    col3.metric("💬 Total QA Entries", hist_count)
    
    if pdf_count == 0:
        st.warning("⚠️ No PDFs uploaded yet. Upload PDFs first to enable rebuilding.")
    st.markdown("### 🔄 Rebuild FAISS (Re-index all PDFs)")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔨 Rebuild Now") and pdf_count > 0:  
            with st.spinner("Rebuilding..."):
                ok, msg = build_faiss_from_pdfs()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        elif pdf_count == 0:
            st.info("📤 Upload PDFs to enable this feature.")

def render_upload_pdf(user_id=None):
    st.subheader("📤 Upload PDFs")  
    uploaded = st.file_uploader("Choose PDF(s) to upload", accept_multiple_files=True, type=["pdf"], help="Drag and drop or click to select PDFs")
    if uploaded:
        os.makedirs(DATA_DIR, exist_ok=True)
        saved_paths = []
        conn = get_db_conn()
        cur = conn.cursor()
        for f in uploaded:
            save_name = f.name
            path = os.path.join(DATA_DIR, save_name)
            if os.path.exists(path):
                base, ext = os.path.splitext(save_name)
                save_name = f"{base}_{int(datetime.now().timestamp())}{ext}"
                path = os.path.join(DATA_DIR, save_name)
            with open(path, "wb") as out:
                out.write(f.read())
            cur.execute("INSERT INTO pdfs (filename, filepath, user_id, uploaded_at) VALUES (?, ?, ?, ?)",
                        (save_name, path, user_id or 0, datetime.now().isoformat()))  
            saved_paths.append(path)
        conn.commit()
        conn.close()
        st.success(f"💾 Saved {len(saved_paths)} PDFs.")
        
        with st.spinner("Rebuilding FAISS…"):
            ok, msg = build_faiss_from_pdfs(user_id)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

def render_manage_pdfs(user_id=None):
    st.subheader("📋 Manage PDFs") 
    conn = get_db_conn()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT id, filename, filepath, uploaded_at FROM pdfs WHERE user_id=? ORDER BY uploaded_at DESC", (user_id,))
    else:
        cur.execute("SELECT id, filename, filepath, uploaded_at FROM pdfs ORDER BY uploaded_at DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        st.info("📭 No PDFs uploaded yet.")
    else:
        for r in rows:
            with st.expander(f"📄 {r['filename']} — {r['uploaded_at'][:16]}", expanded=False):
                cols = st.columns([0.7, 0.2, 0.1])
                cols[0].info(f"Path: {r['filepath']}")
                if cols[1].button("👁️ Preview", key=f"preview_{r['id']}"):
                    try:
                        if os.path.exists(r["filepath"]):
                            with open(r["filepath"], "rb") as f:
                                pdf_bytes = f.read()
                                b64 = base64.b64encode(pdf_bytes).decode()
                        
                            st.components.v1.html(
                                f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" type="application/pdf"></iframe>',
                                height=600
                            )
                        else:
                            st.error("File not found")
                    except Exception as e:
                        st.error(f"Preview failed: {e}. Falling back to download.")
                        
                        try:
                            with open(r["filepath"], "rb") as f:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=f.read(),
                                    file_name=r['filename'],
                                    mime="application/pdf",
                                    key=f"download_{r['id']}"
                                )
                        except Exception as dl_e:
                            st.error(f"Download also failed: {dl_e}")
                if cols[2].button("🗑️ Delete", key=f"del_{r['id']}"):
                    try:
                        if os.path.exists(r["filepath"]):
                            os.remove(r["filepath"])
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM pdfs WHERE id=?", (r["id"],))
                        conn.commit()
                        conn.close()
                        st.success("Deleted. Rebuilding FAISS...")
                        with st.spinner("Rebuilding..."):
                            ok, msg = build_faiss_from_pdfs(user_id)
                            if ok:
                                st.success(msg)
                            else:
                                st.info(msg)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

def render_users_history():
    st.header("👥 Users & History")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    st.subheader("👤 Registered Users")
    for u in users:
        with st.expander(f"👤 {u['username']} ({u['role']}) — {u['created_at'][:10]}"):
            if st.button(f"📖 View History", key=f"vh_{u['id']}"):
               
                if f"show_history_{u['id']}" not in st.session_state:
                    st.session_state[f"show_history_{u['id']}"] = False
                st.session_state[f"show_history_{u['id']}"] = not st.session_state[f"show_history_{u['id']}"]
            if st.session_state.get(f"show_history_{u['id']}", False):
                cur.execute("SELECT question,answer,created_at,is_bookmark FROM history WHERE user_id=? ORDER BY created_at DESC LIMIT 10", (u['id'],))
                his = cur.fetchall()
                if not his:
                    st.info("No history for this user.")
                else:
                    for h in his:
                        bookmark_emoji = "⭐ " if h['is_bookmark'] else ""
                        st.markdown(f"{bookmark_emoji}**Q:** {h['question'][:100]}... \n**A:** {h['answer'][:200]}... \n* {h['created_at']}*")
                        st.markdown("---")
    conn.close()

def render_model_settings():
    st.header("⚙️ Model Settings")
    s = get_settings()
    col1, col2, col3 = st.columns(3)
    with col1:
        model_sel = st.text_input("🤖 Model name (Gemini)", value=s["model"], placeholder="e.g., gemini-pro")
    with col2:
        k_val = st.number_input("📊 k (docs to retrieve)", min_value=1, max_value=20, value=int(s["k"]))
    with col3:
        chunk_val = st.number_input("🔤 Chunk size", min_value=100, max_value=2000, value=int(s["chunk_size"]))
    if st.button("💾 Save Settings"):
        set_settings(model_sel, int(k_val), int(chunk_val))
        st.success("Settings updated! Rebuild FAISS to apply chunk size changes.")

