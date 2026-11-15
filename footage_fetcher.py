"""Pixabay API footage fetcher + local fallback (zero API option)."""
import requests
import random
import shutil
from pathlib import Path
from typing import List, Dict
from src.config import CONFIG

class FootageFetcher:
    BASE_URL = "https://pixabay.com/api/videos"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or CONFIG.pixabay_api_key
        self.use_local = CONFIG.use_local_fallback
        self.local_library = Path("assets/footage")
        self.session = requests.Session()

        if self.api_key:
            self.session.params = {"key": self.api_key}

    def search_videos(self, query: str, orientation: str = "vertical",
                      min_width: int = 1080, per_page: int = 15) -> List[Dict]:
        """Search Pixabay for videos."""
        if not self.api_key:
            return []

        params = {
            "q": query,
            "orientation": orientation,
            "video_type": "film",
            "per_page": per_page,
            "min_width": min_width,
            "safesearch": "true"
        }
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Pixabay search failed for '{query}': {e}")
            return []

        videos = []
        for hit in data.get("hits", []):
            for file in hit.get("videos", {}).values():
                if file.get("width", 0) >= min_width:
                    videos.append({
                        "id": hit["id"],
                        "url": file["url"],
                        "width": file["width"],
                        "height": file["height"],
                        "duration": hit.get("duration", 0),
                        "preview": hit.get("userImageURL", "")
                    })
                    break
        return videos

    def download_video(self, url: str, output_path: str) -> bool:
        """Download video file."""
        try:
            resp = self.session.get(url, stream=True, timeout=60)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def fetch_for_script(self, script: Dict, output_dir: Path) -> List[str]:
        """Fetch footage matching script + local fallback."""
        search_terms = script.get("search_terms", [])

        if script.get("niche") == "ai_tools":
            tool = script.get("tool", {})
            search_terms.extend(tool.get("pexels_terms", []))
        elif script.get("niche") == "psychology":
            topic_data = script.get("topic_data", {})
            search_terms.extend(topic_data.get("pexels_terms", []))

        search_terms = list(dict.fromkeys(search_terms))
        all_clips = []
        needed = CONFIG.footage_max_clips

        if self.api_key:
            for term in search_terms:
                if len(all_clips) >= needed:
                    break
                videos = self.search_videos(term, "vertical", CONFIG.footage_min_width)
                for video in videos:
                    if len(all_clips) >= needed:
                        break
                    min_dur, max_dur = CONFIG.clip_duration_range
                    if min_dur <= video["duration"] <= max_dur:
                        all_clips.append(video)

        output_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []

        for i, clip in enumerate(all_clips):
            if len(downloaded) >= needed:
                break
            output_path = output_dir / f"clip_{i:02d}.mp4"
            if self.download_video(clip["url"], str(output_path)):
                downloaded.append(str(output_path))
                print(f"Downloaded Pixabay clip {len(downloaded)}/{needed}")

        if len(downloaded) < CONFIG.footage_min_clips and self.use_local:
            local_clips = self._fetch_local_fallback(script, output_dir,
                                                      CONFIG.footage_min_clips - len(downloaded))
            downloaded.extend(local_clips)

        if len(downloaded) < CONFIG.footage_min_clips:
            placeholder_clips = self._create_placeholders(output_dir,
                                                          CONFIG.footage_min_clips - len(downloaded))
            downloaded.extend(placeholder_clips)

        return downloaded

    def _fetch_local_fallback(self, script: Dict, output_dir: Path, needed: int) -> List[str]:
        """Use local footage library."""
        niche = script.get("niche", "ai_tools")
        niche_dir = self.local_library / niche

        if not niche_dir.exists():
            niche_dir = self.local_library / "fallback"
            niche_dir.mkdir(parents=True, exist_ok=True)

        clips = list(niche_dir.glob("*.mp4")) + list(niche_dir.glob("*.mov")) + list(niche_dir.glob("*.webm"))
        if not clips:
            return []

        random.shuffle(clips)
        selected = clips[:needed]

        copied = []
        for i, clip in enumerate(selected):
            dest = output_dir / f"local_{len(downloaded)+i:02d}.mp4"
            shutil.copy2(clip, dest)
            copied.append(str(dest))
            print(f"Using local footage: {clip.name}")

        return copied

    def _create_placeholders(self, output_dir: Path, needed: int) -> List[str]:
        """Generate synthetic clips with FFmpeg."""
        import subprocess
        output_dir.mkdir(parents=True, exist_ok=True)
        clips = []

        colors = {
            "ai_tools": ["0x0F172A", "0x1E1E3F", "0x3B006E", "0x00D4FF", "0x7C3AED"],
            "psychology": ["0x1A1A2E", "0x2D1B3D", "0x6A0D4D", "0xF472B6", "0xA78BFA"]
        }
        niche = "ai_tools"
        color_list = colors.get(niche, colors["ai_tools"])

        for i in range(min(needed, len(color_list))):
            output_path = output_dir / f"placeholder_{i:02d}.mp4"
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                f"color=c={color_list[i]}:size=1080x1920:rate=30",
                "-t", "5", "-c:v", "libx264", "-preset", "ultrafast",
                str(output_path)
            ]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0 and output_path.exists():
                clips.append(str(output_path))
                print(f"Generated placeholder clip {i+1}")

        return clips