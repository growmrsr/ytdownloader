import streamlit as st
import yt_dlp
import os
import glob
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Setup Google Drive API Connection
FOLDER_ID = "YOUR_SHARED_GOOGLE_DRIVE_FOLDER_ID_HERE"

def get_drive_service():
    # Streamlit secrets will securely hold your JSON key credentials
    gcp_info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(gcp_info)
    return build('drive', 'v3', credentials=credentials)

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

# Initialize session state tracking for local downloads
if "local_file_data" not in st.session_state:
    st.session_state.local_file_data = None
if "local_file_name" not in st.session_state:
    st.session_state.local_file_name = None
if "prev_url" not in st.session_state:
    st.session_state.prev_url = ""

# Automatically clear cache if the user changes the link
if video_url != st.session_state.prev_url:
    st.session_state.local_file_data = None
    st.session_state.local_file_name = None
    st.session_state.prev_url = video_url

# Arrange buttons neatly side-by-side
col1, col2 = st.columns(2)

# --- BUTTON 1: DOWNLOAD & UPLOAD TO DRIVE ---
with col1:
    if st.button("🚀 Download & Upload to Drive", use_container_width=True):
        if video_url:
            with st.spinner("Processing for Google Drive..."):
                try:
                    ydl_opts = {
                        'outtmpl': '%(id)s.%(ext)s',
                        'format': 'best',
                        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                        'nocheckcertificate': True
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        if not info:
                            raise Exception("Download blocked or failed.")
                        
                        video_id = info.get('id')
                        downloaded_files = glob.glob(f"{video_id}.*")
                        if not downloaded_files:
                            raise FileNotFoundError("The video file was not found on the server.")
                        
                        filename = downloaded_files[0]
                        ext = filename.split('.')[-1]
                        raw_title = info.get('title', video_id)
                        clean_title = "".join(c for c in raw_title if c.isalnum() or c in " ._-()")
                        drive_name = f"{clean_title}.{ext}"
                    
                    st.info("Video downloaded. Uploading to Google Drive...")
                    upload_to_drive(filename, drive_name)
                    
                    if os.path.exists(filename):
                        os.remove(filename)
                        
                    st.success(f"🎉 Success! '{drive_name}' has been saved to your Google Drive.")
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a valid link first.")

# --- BUTTON 2: FETCH FOR LOCAL DEVICE DOWNLOAD ---
with col2:
    if st.button("📥 Fetch for Local Download", use_container_width=True):
        if video_url:
            with st.spinner("Fetching video from YouTube..."):
                try:
                    ydl_opts = {
                        'outtmpl': '%(id)s.%(ext)s',
                        'format': 'best',
                        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                        'nocheckcertificate': True
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        if not info:
                            raise Exception("Download blocked or failed.")
                        
                        video_id = info.get('id')
                        downloaded_files = glob.glob(f"{video_id}.*")
                        if not downloaded_files:
                            raise FileNotFoundError("The video file was not found on the server.")
                        
                        filename = downloaded_files[0]
                        ext = filename.split('.')[-1]
                        raw_title = info.get('title', video_id)
                        clean_title = "".join(c for c in raw_title if c.isalnum() or c in " ._-()")
                        drive_name = f"{clean_title}.{ext}"
                    
                    # Read the binary data into the session state memory
                    with open(filename, "rb") as f:
                        st.session_state.local_file_data = f.read()
                    st.session_state.local_file_name = drive_name
                    
                    # Clean up the cloud server storage immediately
                    if os.path.exists(filename):
                        os.remove(filename)
                        
                    st.success("✨ Video successfully prepared!")
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a valid link first.")

# --- RENDER BROWSER DOWNLOAD LINK IF READY ---
if st.session_state.local_file_data:
    st.write("---")
    st.download_button(
        label=f"💾 Save '{st.session_state.local_file_name}' to Device",
        data=st.session_state.local_file_data,
        file_name=st.session_state.local_file_name,
        mime="video/mp4",
        use_container_width=True
    )
