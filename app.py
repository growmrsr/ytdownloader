import streamlit as st
import requests
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. API Configurations
FOLDER_ID = "1irOJjYYCQPFDRWaEXjfl052d-Rpa2kGf"
COBALT_API_URL = "https://qwkuns.me/api/json"

def get_drive_service():
    # Use OAuth2 instead of a Service Account to utilize your personal storage quota
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

if "local_file_data" not in st.session_state:
    st.session_state.local_file_data = None
if "local_file_name" not in st.session_state:
    st.session_state.local_file_name = None
if "prev_url" not in st.session_state:
    st.session_state.prev_url = ""

if video_url != st.session_state.prev_url:
    st.session_state.local_file_data = None
    st.session_state.local_file_name = None
    st.session_state.prev_url = video_url

def fetch_video_via_cobalt(url):
    """Hits the specified Cobalt API instance to extract the video."""
    api_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # The "alwaysProxy": True is MANDATORY to prevent 0 KB files!
    payload = {
        "url": url,
        "videoQuality": "1080",
        "alwaysProxy": True 
    }
    
    response = requests.post(COBALT_API_URL, headers=api_headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"Cobalt API Error {response.status_code}: {response.text}")
        
    json_response = response.json()
    direct_mp4_link = json_response.get("url") 
    
    if not direct_mp4_link or json_response.get("status") == "error":
        error_text = json_response.get('text', 'Unknown Cobalt API error')
        raise Exception(f"Cobalt failed to extract video: {error_text}")
        
    video_request = requests.get(direct_mp4_link, headers={"User-Agent": api_headers["User-Agent"]})
    video_request.raise_for_status() 
    
    video_data = video_request.content
    
    # Safety check to prevent uploading empty files
    if len(video_data) < 1000:
        raise Exception("Downloaded file is empty or corrupted (0 KB).")
    
    video_id = url.split("/")[-1].split("?")[0]
    clean_name = f"video_{video_id}.mp4"
    
    return video_data, clean_name

col1, col2 = st.columns(2)

# --- BUTTON 1: UPLOAD TO DRIVE ---
with col1:
    if st.button("🚀 Download & Upload to Drive", use_container_width=True):
        if video_url:
            with st.spinner("Extracting via Cobalt API and uploading to Drive..."):
                try:
                    video_bytes, clean_name = fetch_video_via_cobalt(video_url)
                    
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
            with st.spinner("Extracting via Cobalt API..."):
                try:
                    video_bytes, clean_name = fetch_video_via_cobalt(video_url)
                    st.session_state.local_file_data = video_bytes
                    st.session_state.local_file_name = clean_name
                    st.success("✨ Video successfully prepared!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid link.")

if st.session_state.local_file_data:
    st.write("---")
    st.download_button(
        label=f"💾 Save '{st.session_state.local_file_name}' to Device",
        data=st.session_state.local_file_data,
        file_name=st.session_state.local_file_name,
        mime="video/mp4",
        use_container_width=True
    )
