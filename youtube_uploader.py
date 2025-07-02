import requests
import json
import os

def upload_video_to_youtube(video_file_path, title, description, client_id, client_secret, refresh_token):
    # Step 1: Get Access Token
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    token_response = requests.post(token_url, data=payload)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    # Step 2: Upload video
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    upload_url = "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status"

    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22"  # Category ID untuk People & Blogs
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    files = {
        "data": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
        "file": (os.path.basename(video_file_path), open(video_file_path, "rb"), "video/*")
    }

    upload_response = requests.post(upload_url, headers=headers, files=files)
    upload_response.raise_for_status()

    return upload_response.json()
