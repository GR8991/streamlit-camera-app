import streamlit as st
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Chat App", layout="wide", initial_sidebar_state="expanded")

# Initialize Firebase with proper error handling
firebase_initialized = False

try:
    # Check if Firebase is already initialized
    firebase_app = firebase_admin.get_app()
    firebase_initialized = True
except ValueError:
    # Firebase not initialized, do it now
    try:
        firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if not firebase_project_id:
            st.error("❌ Firebase credentials not found!")
            st.info("""
            **Setup Instructions:**
            1. Go to Firebase Console
            2. Get your Service Account Key (JSON)
            3. Create a `.env` file with your credentials
            4. Add to Streamlit Cloud Secrets
            """)
            st.stop()
        
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
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
        firebase_initialized = True
        
    except Exception as e:
        st.error(f"❌ Firebase Error: {str(e)}")
        st.stop()

# Title
st.title("💬 Streamlit Chat App")

# Sidebar for user setup
with st.sidebar:
    st.header("⚙️ User Setup")
    
    username = st.text_input("Enter your name:", placeholder="e.g., John", key="username_input")
    recipient = st.text_input("Friend's name:", placeholder="e.g., Jane", key="recipient_input")
    
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
    
    # Auto-refresh interval
    st.subheader("🔄 Auto-Refresh")
    refresh_interval = st.slider("Refresh every (seconds):", 1, 10, 2, key="refresh_slider")
    
    st.divider()
    
    st.caption("Built with Streamlit + Firebase")

# Check if user is logged in
if not username or not recipient:
    st.warning("⚠️ Please enter your name and friend's name in the sidebar to start chatting!")
    st.stop()

# Display chat messages
st.subheader(f"💬 Chat with {recipient}")

# Fetch messages from Firebase
def get_messages():
    try:
        if not firebase_initialized:
            return []
        
        ref = db.reference(f"chats/{username}_{recipient}")
        messages = ref.get() or {}
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages.items(), key=lambda x: x[1].get('timestamp', 0))
        return sorted_messages
    except Exception as e:
        st.warning(f"Error fetching messages: {e}")
        return []

# Display messages in a container
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
            with st.chat_message("user"):
                st.write(f"**{text}**")
                st.caption(time_str)
        else:
            # Friend's message (left side)
            with st.chat_message("assistant"):
                st.write(f"**{text}**")
                st.caption(time_str)
else:
    st.info("📝 No messages yet. Start a conversation!")

st.divider()

# Input message
st.subheader("Send Message")

col1, col2 = st.columns([4, 1])

with col1:
    message = st.text_input("Type your message:", placeholder="Say something...", key="message_input")

with col2:
    send_button = st.button("Send 📤", use_container_width=True)

# Send message
if send_button and message:
    if not firebase_initialized:
        st.error("❌ Firebase not initialized. Check your credentials.")
    else:
        try:
            timestamp = datetime.now().timestamp()
            
            # Store message in Firebase
            chat_path = f"chats/{username}_{recipient}"
            msg_ref = db.reference(chat_path)
            
            new_msg = {
                'sender': username,
                'text': message,
                'timestamp': timestamp
            }
            
            # Push message to Firebase
            msg_ref.push(new_msg)
            
            st.success("✅ Message sent!")
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error sending message: {str(e)}")

# Auto-refresh using Streamlit's built-in mechanism
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = current_time
    st.rerun()
