import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

# Set page config
st.set_page_config(page_title="Camera App", layout="wide")

st.title("📷 Educational Camera Application")
st.markdown("---")

# Description
st.write("""
This is a simple educational Streamlit app that demonstrates how to access your camera.
**Note:** Your browser will ask for permission to access your camera when you click START.
""")

# Sidebar instructions
with st.sidebar:
    st.header("ℹ️ Instructions")
    st.write("""
    1. Click the **START** button below
    2. Allow camera access when prompted by your browser
    3. Your camera feed will appear
    4. Click **STOP** to turn it off
    """)
    
    st.divider()
    st.subheader("Privacy & Security")
    st.info("""
    ✅ Camera access requires your explicit permission
    ✅ Video is NOT recorded or stored
    ✅ Only visible in your browser session
    """)

# RTC configuration (for WebRTC to work)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Create webrtc streamer
webrtc_ctx = webrtc_streamer(
    key="camera-stream",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={
        "video": True,  # Enable video
        "audio": False  # Disable audio (you can change to True if needed)
    },
    async_processing=True,
)

# Display status
col1, col2, col3 = st.columns(3)

with col1:
    if webrtc_ctx.state.playing:
        st.success("✅ Camera is ACTIVE")
    else:
        st.info("⏸️ Camera is INACTIVE")

with col2:
    st.write(f"**Status:** {'Playing' if webrtc_ctx.state.playing else 'Stopped'}")

with col3:
    if webrtc_ctx.state.playing:
        st.caption("💡 Click STOP above to disable camera")
    else:
        st.caption("💡 Click START above to enable camera")

st.divider()

# Additional features (optional)
st.subheader("📊 About This App")
st.write("""
- Built with **Streamlit** and **streamlit-webrtc**
- Works on desktop and mobile browsers
- Real-time camera streaming via WebRTC
- No data is stored or recorded
""")

# Footer
st.divider()
st.caption("🔒 This app respects your privacy. Camera access requires your permission.")
