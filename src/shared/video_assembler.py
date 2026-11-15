"""FFmpeg video assembler for 9:16 Shorts."""
import subprocess
import os
from pathlib import Path
from typing import List
from src.config import CONFIG

class VideoAssembler:
    def __init__(self):
        self.width = CONFIG.video_width
        self.height = CONFIG.video_height
        self.fps = CONFIG.fps
        self.crf = CONFIG.crf
        self.preset = CONFIG.preset
        self.font_size = CONFIG.font_size
        self.font_color = CONFIG.font_color
        self.stroke_color = CONFIG.stroke_color
        self.stroke_width = CONFIG.stroke_width
        self.safe_margin = CONFIG.safe_zone_margin

    def assemble(self, clips: List[str], audio_path: str, srt_path: str,
                 output_path: str, bgm_path: str = None) -> bool:
        if not clips:
            print("No clips to assemble")
            return False

        filter_parts = []
        input_args = []

        for i, clip in enumerate(clips):
            input_args.extend(["-i", clip])

        audio_input_idx = len(clips)
        input_args.extend(["-i", audio_path])

        bgm_input_idx = None
        if bgm_path and os.path.exists(bgm_path):
            bgm_input_idx = len(clips) + 1
            input_args.extend(["-i", bgm_path])

        video_filter = self._build_video_filter(len(clips))
        filter_parts.append(video_filter)

        subtitle_filter = (
            f"[{len(clips)}:v]subtitles='{srt_path}':"
            f"force_style='FontSize={self.font_size},"
            f"PrimaryColour=&H{self._hex_to_ass(self.font_color)},"
            f"OutlineColour=&H{self._hex_to_ass(self.stroke_color)},"
            f"Outline={self.stroke_width},MarginV={self.safe_margin}'[vout]"
        )
        filter_parts.append(subtitle_filter)

        if bgm_input_idx is not None:
            audio_filter = (
                f"[{audio_input_idx}:a]volume=1.0[nar];"
                f"[{bgm_input_idx}:a]volume={CONFIG.bgm_volume},"
                f"aloop=loop=-1:size=2e+09[bgm];"
                f"[nar][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]"
            )
        else:
            audio_filter = f"[{audio_input_idx}:a]anull[aout]"
        filter_parts.append(audio_filter)

        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            *input_args,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", self.preset, "-crf", str(self.crf),
            "-c:a", "aac", "-b:a", "128k",
            "-r", str(self.fps),
            "-movflags", "+faststart",
            "-shortest",
            output_path
        ]

        print(f"Running FFmpeg with {len(clips)} clips...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False

        print(f"Video assembled: {output_path}")
        return True

    def _build_video_filter(self, num_clips: int) -> str:
        if num_clips == 1:
            return (
                f"[0:v]scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height}[vconcat]"
            )
        else:
            parts = []
            for i in range(num_clips):
                parts.append(
                    f"[{i}:v]scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                    f"crop={self.width}:{self.height}[v{i}]"
                )
            concat_inputs = "".join(f"[v{i}]" for i in range(num_clips))
            parts.append(f"{concat_inputs}concat=n={num_clips}:v=1:a=0[vconcat]")
            return ";".join(parts)

    def _hex_to_ass(self, color: str) -> str:
        color = color.lstrip("#")
        if len(color) == 6:
            r, g, b = color[0:2], color[2:4], color[4:6]
            return f"&H{b}{g}{r}"
        return "&HFFFFFF"

def create_vertical_video(clips: List[str], audio_path: str, srt_path: str,
                          output_path: str, bgm_path: str = None) -> bool:
    assembler = VideoAssembler()
    return assembler.assemble(clips, audio_path, srt_path, output_path, bgm_path)