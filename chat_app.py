import streamlit as st
import firebase_admin
from firebase_admin import db
from datetime import datetime
import time
from streamlit_autorefresh import rerun_script
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
if not firebase_admin.get_app():
    cred = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("FIREBASE_CERT_URL")
    })
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })

st.set_page_config(page_title="Chat App", layout="wide", initial_sidebar_state="expanded")

# Title
st.title("💬 Streamlit Chat App")

# Sidebar for user setup
with st.sidebar:
    st.header("⚙️ User Setup")
    
    username = st.text_input("Enter your name:", placeholder="e.g., John")
    recipient = st.text_input("Friend's name:", placeholder="e.g., Jane")
    
    if username and recipient:
        st.success(f"✅ You: {username}")
        st.info(f"📞 Chatting with: {recipient}")
    
    st.divider()
    
    st.subheader("📋 How It Works")
    st.write("""
    1. Enter your name
    2. Enter friend's name
    3. Type message and send
    4. Messages sync in real-time
    5. Works across different networks!
    """)
    
    st.divider()
    
    # Auto-refresh
    st.subheader("🔄 Auto-Refresh")
    refresh_interval = st.slider("Refresh messages every (seconds):", 1, 10, 2)
    
    st.divider()
    
    st.caption("Built with Streamlit + Firebase")

# Check if user is logged in
if not username or not recipient:
    st.warning("⚠️ Please enter your name and friend's name in the sidebar to start chatting!")
    st.stop()

# Display chat messages
st.subheader(f"💬 Chat with {recipient}")

chat_container = st.container()

# Fetch messages from Firebase
def get_messages():
    try:
        ref = db.reference(f"chats/{username}_{recipient}")
        messages = ref.get() or {}
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages.items(), key=lambda x: x[1].get('timestamp', 0))
        return sorted_messages
    except:
        return []

# Display messages
with chat_container:
    messages = get_messages()
    
    if messages:
        for msg_id, msg_data in messages:
            sender = msg_data.get('sender', 'Unknown')
            text = msg_data.get('text', '')
            timestamp = msg_data.get('timestamp', '')
            
            # Format timestamp
            try:
                time_obj = datetime.fromtimestamp(timestamp)
                time_str = time_obj.strftime("%H:%M")
            except:
                time_str = "Now"
            
            # Display message
            if sender == username:
                # Your message (right side)
                st.chat_message("user").write(f"**{text}**\n\n*{time_str}*")
            else:
                # Friend's message (left side)
                st.chat_message("assistant").write(f"**{text}**\n\n*{time_str}*")
    else:
        st.info("📝 No messages yet. Start a conversation!")

st.divider()

# Input message
st.subheader("Send Message")

col1, col2 = st.columns([4, 1])

with col1:
    message = st.text_input("Type your message:", placeholder="Say something...")

with col2:
    send_button = st.button("Send 📤", use_container_width=True)

# Send message
if send_button and message:
    try:
        timestamp = datetime.now().timestamp()
        
        # Store message in both directions for easy retrieval
        chat_path = f"chats/{username}_{recipient}"
        msg_ref = db.reference(chat_path)
        
        new_msg = {
            'sender': username,
            'text': message,
            'timestamp': timestamp
        }
        
        # Push message
        msg_ref.push(new_msg)
        
        st.success("✅ Message sent!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error sending message: {e}")

# Auto-refresh
import streamlit as st
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = current_time
    st.rerun()
