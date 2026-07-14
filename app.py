import streamlit as st
import requests

st.title("⚡ Server-to-Drive Downloader")
st.write("Enter a YouTube link. The background engine will process it securely onto your Google Drive.")

# A text field where you can paste the new dynamic Ngrok URL whenever you spin up the Colab backend
backend_url = st.text_input("Backend Engine URL:", placeholder="https://xxxx.ngrok-free.app")
video_url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🚀 Process & Upload to Drive", use_container_width=True):
    if video_url and backend_url:
        with st.spinner("Server is downloading video via Google cloud pipes..."):
            try:
                # Format endpoint target cleanly
                endpoint = f"{backend_url.strip('/')}/download"
                response = requests.post(endpoint, json={"url": video_url}, timeout=120)
                
                result = response.json()
                if response.status_code == 200 and result.get("status") == "success":
                    st.success(f"🎉 Success! '{result.get('filename')}' is safely in your Google Drive.")
                else:
                    st.error(f"Engine Error: {result.get('message')}")
            except Exception as e:
                st.error(f"Could not connect to backend server: {str(e)}")
    else:
        st.warning("Please provide both the Backend Engine URL and a Video URL.")
