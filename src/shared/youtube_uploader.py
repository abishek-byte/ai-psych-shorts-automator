"""YouTube Data API uploader for Shorts."""
import os
import json
from pathlib import Path
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import google.oauth2.credentials
from src.config import CONFIG

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    def __init__(self):
        self.client_secrets_json = CONFIG.youtube_client_secrets
        self.token_json = CONFIG.youtube_token
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        creds = None

        if self.token_json:
            creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
                json.loads(self.token_json), SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            if not self.client_secrets_json:
                raise ValueError("YouTube auth required. Run locally first to generate token.")
            flow = InstalledAppFlow.from_client_config(
                json.loads(self.client_secrets_json), SCOPES)
            creds = flow.run_local_server(port=0)
            print(f"Save this as YOUTUBE_TOKEN secret:\n{creds.to_json()}")

        self.youtube = build("youtube", "v3", credentials=creds)

    def upload_short(self, video_path: str, thumbnail_path: str, script: Dict) -> Optional[str]:
        title = f"{script.get('title', 'Daily Short')} {CONFIG.shorts_hashtag}"
        description = self._build_description(script)
        tags = CONFIG.default_tags + script.get("hashtags", [])

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:30],
                "categoryId": CONFIG.category_id,
                "defaultLanguage": CONFIG.language,
            },
            "status": {
                "privacyStatus": CONFIG.privacy_status,
                "selfDeclaredMadeForKids": False,
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        print(f"Uploaded: https://youtube.com/shorts/{video_id}")

        if thumbnail_path and os.path.exists(thumbnail_path):
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print("Thumbnail uploaded")

        return video_id

    def _build_description(self, script: Dict) -> str:
        niche = script.get("niche", "")
        desc_parts = [
            script.get("title", ""),
            "",
            "Subscribe for daily insights!",
            "",
        ]

        if niche == "ai_tools":
            tool = script.get("tool", {})
            desc_parts.extend([
                f"Tool: {tool.get('name', '')}",
                f"Category: {tool.get('category', '')}",
                f"Free tier: {tool.get('free_tier', '')}",
                "",
            ])
        elif niche == "psychology":
            topic = script.get("topic_data", {}).get("topic", "")
            desc_parts.extend([
                f"Topic: {topic}",
                f"Category: {script.get('topic_data', {}).get('category', '')}",
                "",
            ])

        desc_parts.extend([
            "#Shorts #AI #Psychology #Productivity #SelfImprovement",
            "",
            "Background music from YouTube Audio Library",
            "Footage from Pexels (CC0)",
        ])

        return "\n".join(desc_parts)

def upload_video(video_path: str, thumbnail_path: str, script: Dict) -> Optional[str]:
    uploader = YouTubeUploader()
    return uploader.upload_short(video_path, thumbnail_path, script)