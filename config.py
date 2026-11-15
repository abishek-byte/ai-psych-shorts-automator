"""Central configuration loader."""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Config:
    # API Keys (from environment/secrets)
    groq_api_key: str = ""
    pixabay_api_key: str = ""
    youtube_client_secrets: str = ""
    youtube_token: str = ""

    # Channel
    channel_name: str = "AI & Psychology Daily"
    channel_description: str = ""
    default_tags: list = None
    category_id: str = "27"
    language: str = "en"
    privacy_status: str = "public"

    # Niches
    niches: Dict[str, Any] = None

    # Production
    video_width: int = 1080
    video_height: int = 1920
    fps: int = 30
    crf: int = 23
    preset: str = "fast"
    font_size: int = 72
    font_color: str = "white"
    stroke_color: str = "black"
    stroke_width: int = 3
    safe_zone_margin: int = 150

    tts_voice: str = "en-US-AriaNeural"
    tts_rate: str = "+5%"
    tts_volume: str = "+0%"
    bgm_volume: float = 0.12
    bgm_tracks: list = None

    footage_min_clips: int = 3
    footage_max_clips: int = 6
    clip_duration_range: list = None
    footage_orientation: str = "vertical"
    footage_min_width: int = 1080
    use_local_fallback: bool = True

    thumbnail_width: int = 1280
    thumbnail_height: int = 720
    title_font_size: int = 80
    subtitle_font_size: int = 48
    background_style: str = "gradient"

    upload_max_per_day: int = 2
    shorts_hashtag: str = "#Shorts"
    add_to_shorts_shelf: bool = True
    notify_subscribers: bool = False

    def __post_init__(self):
        if self.default_tags is None:
            self.default_tags = ["shorts", "ai", "psychology", "productivity", "selfimprovement"]
        if self.bgm_tracks is None:
            self.bgm_tracks = ["assets/bgm/upbeat.mp3", "assets/bgm/calm.mp3"]
        if self.clip_duration_range is None:
            self.clip_duration_range = [3, 8]

def load_config() -> Config:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    cfg = Config()

    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        ch = data.get("channel", {})
        cfg.channel_name = ch.get("name", cfg.channel_name)
        cfg.channel_description = ch.get("description", cfg.channel_description)
        cfg.default_tags = ch.get("default_tags", cfg.default_tags)
        cfg.category_id = ch.get("category_id", cfg.category_id)
        cfg.language = ch.get("language", cfg.language)
        cfg.privacy_status = ch.get("privacy_status", cfg.privacy_status)

        cfg.niches = data.get("niches", {})

        prod = data.get("production", {})
        vid = prod.get("video", {})
        cfg.video_width = vid.get("width", cfg.video_width)
        cfg.video_height = vid.get("height", cfg.video_height)
        cfg.fps = vid.get("fps", cfg.fps)
        cfg.crf = vid.get("crf", cfg.crf)
        cfg.preset = vid.get("preset", cfg.preset)
        cfg.font_size = vid.get("font_size", cfg.font_size)
        cfg.font_color = vid.get("font_color", cfg.font_color)
        cfg.stroke_color = vid.get("stroke_color", cfg.stroke_color)
        cfg.stroke_width = vid.get("stroke_width", cfg.stroke_width)
        cfg.safe_zone_margin = vid.get("safe_zone_margin", cfg.safe_zone_margin)

        aud = prod.get("audio", {})
        cfg.tts_voice = aud.get("tts_voice", cfg.tts_voice)
        cfg.tts_rate = aud.get("tts_rate", cfg.tts_rate)
        cfg.tts_volume = aud.get("tts_volume", cfg.tts_volume)
        cfg.bgm_volume = aud.get("bgm_volume", cfg.bgm_volume)
        cfg.bgm_tracks = aud.get("bgm_tracks", cfg.bgm_tracks)

        ftg = prod.get("footage", {})
        cfg.footage_min_clips = ftg.get("min_clips", cfg.footage_min_clips)
        cfg.footage_max_clips = ftg.get("max_clips", cfg.footage_max_clips)
        cfg.clip_duration_range = ftg.get("clip_duration_range", cfg.clip_duration_range)
        cfg.footage_orientation = ftg.get("orientation", cfg.footage_orientation)
        cfg.footage_min_width = ftg.get("min_width", cfg.footage_min_width)
        cfg.use_local_fallback = ftg.get("use_local_fallback", cfg.use_local_fallback)

        thumb = prod.get("thumbnail", {})
        cfg.thumbnail_width = thumb.get("width", cfg.thumbnail_width)
        cfg.thumbnail_height = thumb.get("height", cfg.thumbnail_height)
        cfg.title_font_size = thumb.get("title_font_size", cfg.title_font_size)
        cfg.subtitle_font_size = thumb.get("subtitle_font_size", cfg.subtitle_font_size)
        cfg.background_style = thumb.get("background_style", cfg.background_style)

        up = data.get("upload", {})
        cfg.upload_max_per_day = up.get("max_per_day", cfg.upload_max_per_day)
        cfg.shorts_hashtag = up.get("shorts_hashtag", cfg.shorts_hashtag)
        cfg.add_to_shorts_shelf = up.get("add_to_shorts_shelf", cfg.add_to_shorts_shelf)
        cfg.notify_subscribers = up.get("notify_subscribers", cfg.notify_subscribers)

    # Override with environment variables (GitHub Secrets)
    cfg.groq_api_key = os.getenv("GROQ_API_KEY", cfg.groq_api_key)
    cfg.pixabay_api_key = os.getenv("PIXABAY_API_KEY", cfg.pixabay_api_key)
    cfg.youtube_client_secrets = os.getenv("YOUTUBE_CLIENT_SECRETS", cfg.youtube_client_secrets)
    cfg.youtube_token = os.getenv("YOUTUBE_TOKEN", cfg.youtube_token)

    return cfg

CONFIG = load_config()