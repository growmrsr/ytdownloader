import streamlit as st
import os
from pytubefix import YouTube
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. API & Folder Configurations
FOLDER_ID = "1irOJjYYCQPFDRWaEXjfl052d-Rpa2kGf"

def get_drive_service():
    oauth_info = st.secrets["gcp_oauth"]
    creds = Credentials(
        token=None,
        refresh_token=oauth_info["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=oauth_info["client_id"],
        client_secret=oauth_info["client_secret"]
    )
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, file_name):
    service = get_drive_service()
    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# 2. Web Interface Configuration
st.title("⚡ Direct Video Downloader")
st.write("Paste a link below to send the video to Google Drive or download it directly to your device.")

video_url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# Initialize session states for storing file bytes cleanly inside Streamlit
if "local_file_data" not in st.session_state:
    st.session_state.local_file_data = None
if "local_file_name" not in st.session_state:
    st.session_state.local_file_name = None
if "prev_url" not in st.session_state:
    st.session_state.prev_url = ""

# Reset state if the user pastes a new URL link
if video_url != st.session_state.prev_url:
    st.session_state.local_file_data = None
    st.session_state.local_file_name = None
    st.session_state.prev_url = video_url

def download_video_via_pytubefix(url):
    """Downloads highest resolution progressive MP4 stream directly using pytubefix."""
    try:
        # Initializing the YouTube handler object
        yt = YouTube(url)
        
        # Grabbing the highest resolution progressive stream (contains both video and audio tracks)
        stream = yt.streams.get_highest_resolution()
        if not stream:
            raise Exception("No stable progressive video stream found.")
            
        clean_name = f"{yt.title}.mp4".replace("/", "_").replace("\\", "_")
        
        # Download file directly to local instance storage environment
        temp_path = stream.download(output_path=".", filename="temp_download_target.mp4")
        
        with open(temp_path, "rb") as f:
            video_bytes = f.read()
            
        # Clean up local system storage immediately
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return video_bytes, clean_name
    except Exception as e:
        raise Exception(f"Pytubefix processing failed: {str(e)}")

col1, col2 = st.columns(2)

# --- BUTTON 1: UPLOAD TO DRIVE ---
with col1:
    if st.button("🚀 Download & Upload to Drive", use_container_width=True):
        if video_url:
            with st.spinner("Processing video and uploading to Google Drive..."):
                try:
                    video_bytes, clean_name = download_video_via_pytubefix(video_url)
                    
                    temp_filename = "temp_video.mp4"
                    with open(temp_filename, "wb") as f:
                        f.write(video_bytes)
                        
                    upload_to_drive(temp_filename, clean_name)
                    
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                        
                    st.success(f"🎉 Success! '{clean_name}' saved to Google Drive.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid link.")

# --- BUTTON 2: LOCAL DOWNLOAD ---
with col2:
    if st.button("📥 Fetch for Local Download", use_container_width=True):
        if video_url:
            with st.spinner("Processing video..."):
                try:
                    video_bytes, clean_name = download_video_via_pytubefix(video_url)
                    st.session_state.local_file_data = video_bytes
                    st.session_state.local_file_name = clean_name
                    st.success("✨ Video successfully prepared!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid link.")

# Displays secondary download trigger if local data preparation succeeded
if st.session_state.local_file_data:
    st.write("---")
    st.download_button(
        label=f"💾 Save '{st.session_state.local_file_name}' to Device",
        data=st.session_state.local_file_data,
        file_name=st.session_state.local_file_name,
        mime="video/mp4",
        use_container_width=True
    )
