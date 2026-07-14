import streamlit as st
import yt_dlp
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Setup Google Drive API Connection
FOLDER_ID = "https://drive.google.com/drive/folders/1irOJjYYCQPFDRWaEXjfl052d-Rpa2kGf?usp=drive_link"

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
                # Download file locally to the hosting server
                ydl_opts = {
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'format': 'best',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    filename = ydl.prepare_filename(info)
                    clean_name = os.path.basename(filename)
                
                st.info("Video downloaded to server. Uploading to Google Drive...")
                
                # Upload to Google Drive
                upload_to_drive(filename, clean_name)
                
                # Clean up server storage
                os.remove(filename)
                
                st.success(f"🎉 Success! '{clean_name}' has been saved to your Google Drive.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid link first.")