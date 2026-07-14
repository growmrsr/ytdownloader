import streamlit as st
import yt_dlp
import os
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

# 2. Web Interface
st.title("⚡ Direct Video Downloader")
st.write("Paste a link below to send the video directly to Google Drive.")

video_url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download & Upload"):
    if video_url:
        with st.spinner("Processing... This might take a minute for large files."):
            try:
                # 1. Save locally using the Video ID to avoid special character errors
                ydl_opts = {
                    'outtmpl': '%(id)s.%(ext)s',
                    'format': 'best',
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                    'nocheckcertificate': True,
                    'ignoreerrors': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    
                    if not info:
                        raise Exception("Download blocked. The video might be private or age-restricted.")
                    
                    # 2. Get the exact, final filename SAFELY to avoid KeyError
                    filename = ydl.prepare_filename(info)
                    
                    if 'requested_downloads' in info and info['requested_downloads']:
                        # Using .get() prevents the script from crashing if 'filepath' is missing
                        actual_path = info['requested_downloads'][0].get('filepath')
                        if actual_path:
                            filename = actual_path
                    elif '_filename' in info:
                        filename = info['_filename']
                    
                    # 3. Create a clean, readable name for Google Drive
                    ext = filename.split('.')[-1]
                    raw_title = info.get('title', info.get('id', 'Video'))
                    
                    # Strip out weird characters but keep letters, numbers, and spaces
                    clean_title = "".join(c for c in raw_title if c.isalnum() or c in " ._-()")
                    drive_name = f"{clean_title}.{ext}"
                
                st.info("Video downloaded to server. Uploading to Google Drive...")
                
                # Upload to Google Drive using the clean name
                upload_to_drive(filename, drive_name)
                
                # Clean up server storage
                if os.path.exists(filename):
                    os.remove(filename)
                
                st.success(f"🎉 Success! '{drive_name}' has been saved to your Google Drive.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid link first.")import streamlit as st
import yt_dlp
import os
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

# 2. Web Interface
st.title("⚡ Direct Video Downloader")
st.write("Paste a link below to send the video directly to Google Drive.")

video_url = st.text_input("Enter Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download & Upload"):
    if video_url:
        with st.spinner("Processing... This might take a minute for large files."):
            try:
                # 1. Save locally using the Video ID to avoid special character errors
                ydl_opts = {
                    'outtmpl': '%(id)s.%(ext)s',
                    'format': 'best',
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                    'nocheckcertificate': True,
                    'ignoreerrors': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    
                    if not info:
                        raise Exception("Download blocked. The video might be private or age-restricted.")
                    
                    # 2. Get the exact, final filename SAFELY to avoid KeyError
                    filename = ydl.prepare_filename(info)
                    
                    if 'requested_downloads' in info and info['requested_downloads']:
                        # Using .get() prevents the script from crashing if 'filepath' is missing
                        actual_path = info['requested_downloads'][0].get('filepath')
                        if actual_path:
                            filename = actual_path
                    elif '_filename' in info:
                        filename = info['_filename']
                    
                    # 3. Create a clean, readable name for Google Drive
                    ext = filename.split('.')[-1]
                    raw_title = info.get('title', info.get('id', 'Video'))
                    
                    # Strip out weird characters but keep letters, numbers, and spaces
                    clean_title = "".join(c for c in raw_title if c.isalnum() or c in " ._-()")
                    drive_name = f"{clean_title}.{ext}"
                
                st.info("Video downloaded to server. Uploading to Google Drive...")
                
                # Upload to Google Drive using the clean name
                upload_to_drive(filename, drive_name)
                
                # Clean up server storage
                if os.path.exists(filename):
                    os.remove(filename)
                
                st.success(f"🎉 Success! '{drive_name}' has been saved to your Google Drive.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid link first.")
