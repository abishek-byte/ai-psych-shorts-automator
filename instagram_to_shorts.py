"""
Instagram Reels → YouTube Shorts Automated Pipeline
Downloads Instagram Reels and uploads as YouTube Shorts.
"""
import asyncio
import os
import json
import subprocess
import yt_dlp
from pathlib import Path
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.oauth2.credentials

# ============ CONFIG ============
INSTAGRAM_URLS = [
    # Add Instagram Reel URLs here
    # "https://www.instagram.com/reel/ABC123/",
]
OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

# YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"


def download_instagram_reel(url: str, output_dir: Path) -> str:
    """Download Instagram Reel using yt-dlp."""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def convert_to_shorts_format(input_path: str, output_path: str) -> bool:
    """Convert video to 9:16 vertical format for Shorts."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_path,
        "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def get_youtube_service():
    """Authenticate and return YouTube service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_to_shorts(youtube, video_path: str, title: str, description: str = "") -> str:
    """Upload video as YouTube Short."""
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": ["shorts", "instagram", "reels"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload: {int(status.progress() * 100)}%")

    return response["id"]


async def process_reel(url: str, youtube) -> bool:
    """Process single Instagram Reel."""
    print(f"\n{'='*50}")
    print(f"Processing: {url}")
    print(f"{'='*50}")

    try:
        # 1. Download
        print("1. Downloading...")
        downloaded = download_instagram_reel(url, OUTPUT_DIR)
        print(f"   Downloaded: {downloaded}")

        # 2. Convert to Shorts format
        print("2. Converting to 9:16...")
        short_path = str(OUTPUT_DIR / f"short_{Path(downloaded).stem}.mp4")
        if not convert_to_shorts_format(downloaded, short_path):
            print("   Conversion failed")
            return False
        print(f"   Converted: {short_path}")

        # 3. Upload
        print("3. Uploading to YouTube Shorts...")
        title = f"Instagram Reel {datetime.now().strftime('%Y-%m-%d %H:%M')} #Shorts"
        video_id = upload_to_shorts(youtube, short_path, title, f"Source: {url}")
        print(f"   Uploaded: https://youtube.com/shorts/{video_id}")

        # 4. Cleanup
        os.remove(downloaded)
        os.remove(short_path)

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


async def main():
    if not INSTAGRAM_URLS:
        print("Add Instagram Reel URLs to INSTAGRAM_URLS list")
        return

    youtube = get_youtube_service()

    for url in INSTAGRAM_URLS:
        await process_reel(url, youtube)
        await asyncio.sleep(2)  # Rate limiting

    print("\n✓ All done!")


if __name__ == "__main__":
    asyncio.run(main())