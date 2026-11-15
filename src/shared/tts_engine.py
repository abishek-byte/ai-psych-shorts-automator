"""Edge TTS - Free Microsoft voices, no API key needed."""
import asyncio
import edge_tts
from pathlib import Path
from typing import List, Dict
from src.config import CONFIG

class TTSEngine:
    def __init__(self):
        self.voice = CONFIG.tts_voice
        self.rate = CONFIG.tts_rate
        self.volume = CONFIG.tts_volume

    async def synthesize(self, text: str, output_path: str) -> Dict:
        """Generate audio + word-level timestamps for subtitles."""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)

        word_timestamps = []
        async for chunk in communicate.stream():
            if chunk["type"] == "WordBoundary":
                word_timestamps.append({
                    "text": chunk["text"],
                    "offset": chunk["offset"] / 10_000_000,
                    "duration": chunk["duration"] / 10_000_000
                })

        await communicate.save(output_path)

        return {
            "audio_path": output_path,
            "word_timestamps": word_timestamps,
            "duration": word_timestamps[-1]["offset"] + word_timestamps[-1]["duration"] if word_timestamps else 0
        }

    def create_srt(self, word_timestamps: List[Dict], output_path: str, max_chars_per_line: int = 42):
        """Generate SRT subtitles from word timestamps."""
        lines = []
        current_line = []
        current_chars = 0
        line_start = 0

        for i, word in enumerate(word_timestamps):
            if not current_line:
                line_start = word["offset"]

            current_line.append(word["text"])
            current_chars += len(word["text"]) + 1

            should_break = (
                word["text"].endswith((".", "!", "?", ",")) or
                current_chars >= max_chars_per_line or
                (i < len(word_timestamps) - 1 and word_timestamps[i+1]["offset"] - word["offset"] > 0.5) or
                i == len(word_timestamps) - 1
            )

            if should_break:
                line_end = word["offset"] + word["duration"]
                lines.append({
                    "start": line_start,
                    "end": line_end,
                    "text": " ".join(current_line)
                })
                current_line = []
                current_chars = 0

        with open(output_path, "w", encoding="utf-8") as f:
            for i, line in enumerate(lines, 1):
                f.write(f"{i}\n")
                f.write(f"{self._format_time(line['start'])} --> {self._format_time(line['end'])}\n")
                f.write(f"{line['text']}\n\n")

        return output_path

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"