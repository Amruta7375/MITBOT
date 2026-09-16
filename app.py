import os
os.environ['CUDA_VISIBLE_DEVICES'] = '' 
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from auth import create_user, authenticate_user, reset_password
from admin import render_dashboard, render_upload_pdf as admin_upload, render_manage_pdfs as admin_manage, render_users_history, render_model_settings
from user_pages import render_chat, render_history, render_bookmarks, render_user_uploads
from utils import PDFKIT_CONFIG
from db import get_db_conn

load_dotenv(find_dotenv())

DATA_DIR = "data"

st.set_page_config(page_title="MITBot (Auth + Admin)", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: #2c3e50;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMarkdown {
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Main Container for Login */
    .main-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: slideUp 0.6s ease-out;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Tab Content */
    .tab-content {
        animation: fadeIn 0.4s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Form Inputs */
    .form-input {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        transition: all 0.3s ease;
        font-size: 1rem;
        background: #fafbfc;
    }
    .form-input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: white;
    }
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Buttons */
    .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.875rem 2rem;
        border-radius: 12px;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: 500;
        font-size: 1rem;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
    }
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        background: linear-gradient(135deg, #5856eb 0%, #7c3aed 100%);
    }
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Role Select */
    .role-select {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        background: #fafbfc;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Sidebar Enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
        padding: 1rem;
    }
    .stSidebar > div {
        padding: 1rem;
    }
    section[data-testid="stSidebar"] {
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 18px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .user .stMarkdown {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1565c0;
        border-radius: 18px;
        padding: 1rem;
    }
    .assistant .stMarkdown {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        color: #4a148c;
        border-radius: 18px;
        padding: 1rem;
    }
    
    /* Expander Styles */
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin: 0.5rem 0;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .stExpander:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        text-align: center;
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #6366f1;
        background: #fafbfc;
    }
    
    /* Attractive Bookmark Buttons */
    .bookmark-btn {
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        color: #333;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(255,215,0,0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .bookmark-btn:hover {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 4px 12px rgba(255,215,0,0.4);
    }
    .bookmark-unfilled {
        background: linear-gradient(45deg, #e5e7eb, #f3f4f6);
        color: #9ca3af;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .bookmark-unfilled:hover {
        background: linear-gradient(45deg, #d1d5db, #e5e7eb);
        color: #6b7280;
    }
    
    /* Success/Error Warnings */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 12px;
        padding: 1rem;
    }
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        border-radius: 12px;
        padding: 1rem;
    }
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-container {
            margin: 1rem;
            padding: 1.5rem;
        }
        .stButton > button {
            padding: 0.75rem 1rem !important;
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5856eb, #7c3aed);
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None 
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.title("🚀 Welcome to MITBot")
        st.markdown("---")
        st.subheader("Your AI-Powered Document Assistant")
        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔒 Forgot Password"])
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.subheader("Login to your account")
            login_user = st.text_input("Username", placeholder="Enter your username", key="login_user", help="Your registered username")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass", help="Your account password")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("Login", use_container_width=True, key="login_btn"):
                    if login_user and login_pass:
                        ok, result = authenticate_user(login_user, login_pass)
                        if ok:
                            st.session_state.user = result
                            
                            if result['role'] == 'admin':
                                st.session_state.admin_mode = "Admin"
                                st.session_state.admin_action = "Dashboard"
                            else:
                                st.session_state.user_page = "💬 Chat"
                            st.success("Logged in successfully! 🎉")
                            st.rerun()
                        else:
                            st.error(result)
                    else:
                        st.error("Please enter username and password.")
            st.markdown("*Don't have an account? Switch to Register tab.*")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.subheader("Create a new account")
            reg_user = st.text_input("New Username", placeholder="Choose a username", key="reg_user", help="Unique username")
            reg_email = st.text_input("Email ID", placeholder="Enter your email", key="reg_email", help="Valid email address")
            reg_pass = st.text_input("New Password", type="password", placeholder="Create a password", key="reg_pass", help="Strong password")
            reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_pass2", help="Re-enter password")
            reg_role = st.selectbox("Role", ["Student", "Admin"], key="reg_role", help="Select your role")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("Register", use_container_width=True, key="reg_btn"):
                    if not all([reg_user, reg_email, reg_pass]):
                        st.error("Please provide all fields.")
                    elif reg_pass != reg_pass2:
                        st.error("Passwords do not match.")
                    else:
                        role_map = {"Student": "user", "Admin": "admin"}
                        ok, msg = create_user(reg_user, reg_email, reg_pass, role=role_map[reg_role])
                        if ok:
                            st.success(msg + f" Role: {reg_role}")
                        else:
                            st.error(msg)
            st.markdown("*Already have an account? Switch to Login tab.*")
            st.markdown('</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            st.subheader("Reset your password")
            reset_email = st.text_input("Email ID", placeholder="Enter your registered email", key="reset_email", help="Email associated with your account")
            reset_pass = st.text_input("New Password", type="password", placeholder="Enter new password", key="reset_pass", help="New strong password")
            reset_pass2 = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password", key="reset_pass2", help="Re-enter new password")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("Reset Password", use_container_width=True, key="reset_btn"):
                    if not all([reset_email, reset_pass]):
                        st.error("Please provide all fields.")
                    elif reset_pass != reset_pass2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = reset_password(reset_email, reset_pass)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
            st.markdown("*Password reset successful. Please login with new password.*")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) 
    st.stop()


with st.sidebar:
    st.title("🤖 MITBot Controls")
    st.markdown(f"**👤 Logged in as:** {st.session_state.user['username']} \n**🎭 Role:** {st.session_state.user['role']}")
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        for key in list(st.session_state.keys()):
            if key not in ["user", "messages"]:
                del st.session_state[key]
        st.rerun()
    st.markdown("---")
  
    role = st.session_state.user["role"]
    user_id = st.session_state.user["id"]
    if role == "admin":
        if "admin_mode" not in st.session_state:
            st.session_state.admin_mode = "Admin" 
        mode = st.selectbox("🎛️ Mode", ["User", "Admin"], index=1 if st.session_state.admin_mode == "Admin" else 0)
        if mode == "Admin":
            if "admin_action" not in st.session_state:
                st.session_state.admin_action = "Dashboard"
            admin_action = st.selectbox("📋 Go to", ["Dashboard", "Upload PDF", "Manage PDFs", "Users & History", "Model Settings"], index=["Dashboard", "Upload PDF", "Manage PDFs", "Users & History", "Model Settings"].index(st.session_state.admin_action))
            st.session_state.admin_mode = "Admin"
            st.session_state.admin_action = admin_action
        else:
            st.session_state.admin_mode = "User"
            if "user_page" not in st.session_state:
                st.session_state.user_page = "💬 Chat"
            page = st.selectbox("📄 Page", ["💬 Chat", "📚 History", "⭐ Bookmarks", "📤 My Uploads"], index=["💬 Chat", "📚 History", "⭐ Bookmarks", "📤 My Uploads"].index(st.session_state.user_page))
            st.session_state.user_page = page
    else:
        if "user_page" not in st.session_state:
            st.session_state.user_page = "💬 Chat"
        page = st.selectbox("📄 Page", ["💬 Chat", "📚 History", "⭐ Bookmarks", "📤 My Uploads"], index=["💬 Chat", "📚 History", "⭐ Bookmarks", "📤 My Uploads"].index(st.session_state.user_page))
        st.session_state.user_page = page
    st.markdown("---")
    
    if PDFKIT_CONFIG:
        st.success("📄 wkhtmltopdf detected")
    else:
        st.warning("⚠️ wkhtmltopdf not found — PDF export may fail")


st.title("💬 MITBot — Document Chat Assistant")
page = st.session_state.get("user_page", "💬 Chat")
admin_mode = st.session_state.get("admin_mode", "User")


if role == "admin" and admin_mode == "Admin":
    admin_action = st.session_state.get("admin_action", "Dashboard")
    if admin_action == "Dashboard":
        render_dashboard()
    elif admin_action == "Upload PDF":
        admin_upload()  
    elif admin_action == "Manage PDFs":
        admin_manage()  
    elif admin_action == "Users & History":
        render_users_history()
    elif admin_action == "Model Settings":
        render_model_settings()
    st.stop()

if page == "💬 Chat":
    render_chat(user_id)
elif page == "📚 History":
    render_history(user_id)
elif page == "⭐ Bookmarks":
    render_bookmarks(user_id)
elif page == "📤 My Uploads":
    render_user_uploads(user_id)