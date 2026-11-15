"""Main pipeline orchestrator."""
import asyncio
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from src.config import CONFIG
from src.shared.llm_client import LLMClient
from src.shared.tts_engine import TTSEngine
from src.shared.footage_fetcher import FootageFetcher
from src.shared.video_assembler import create_vertical_video
from src.shared.thumbnail_maker import make_thumbnail
from src.shared.youtube_uploader import upload_video
from src.niches.ai_tools import AIToolsGenerator
from src.niches.psychology import PsychologyGenerator


class Pipeline:
    def __init__(self, niche: str):
        self.niche = niche
        self.llm = LLMClient()
        self.tts = TTSEngine()
        self.footage = FootageFetcher()
        self.work_dir = Path(f"work/{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.work_dir.mkdir(parents=True, exist_ok=True)

        if niche == "ai_tools":
            self.generator = AIToolsGenerator(self.llm)
            self.style = CONFIG.niches.get("ai_tools", {}).get("prompt_style", "tutorial")
        elif niche == "psychology":
            self.generator = PsychologyGenerator(self.llm)
            self.style = CONFIG.niches.get("psychology", {}).get("prompt_style", "fact")
        else:
            raise ValueError(f"Unknown niche: {niche}")

    async def run(self) -> bool:
        print(f"\n{'='*50}")
        print(f"Starting {self.niche} pipeline")
        print(f"{'='*50}")

        try:
            print("1. Generating script...")
            script = self.generator.generate_script(self.style)
            script_path = self.work_dir / "script.json"
            with open(script_path, "w") as f:
                json.dump(script, f, indent=2)
            print(f"   Topic: {script.get('title', 'Untitled')}")

            print("2. Generating narration...")
            narration_text = self._build_narration(script)
            audio_path = self.work_dir / "narration.wav"
            srt_path = self.work_dir / "narration.srt"

            result = await self.tts.synthesize(narration_text, str(audio_path))
            self.tts.create_srt(result["word_timestamps"], str(srt_path))
            print(f"   Duration: {result['duration']:.1f}s")

            print("3. Fetching footage...")
            clips = self.footage.fetch_for_script(script, self.work_dir / "clips")
            print(f"   Got {len(clips)} clips")

            print("4. Assembling video...")
            video_path = self.work_dir / "output.mp4"

            bgm_path = None
            if CONFIG.bgm_tracks:
                for track in CONFIG.bgm_tracks:
                    if os.path.exists(track):
                        bgm_path = track
                        break

            success = create_vertical_video(
                clips, str(audio_path), str(srt_path), str(video_path), bgm_path
            )
            if not success:
                raise RuntimeError("Video assembly failed")

            print("5. Creating thumbnail...")
            thumb_path = self.work_dir / "thumbnail.jpg"
            bg_frame = self.footage.get_background_frame(clips)
            make_thumbnail(script, str(thumb_path), bg_frame)

            print("6. Uploading to YouTube...")
            video_id = upload_video(str(video_path), str(thumb_path), script)
            if not video_id:
                raise RuntimeError("Upload failed")

            metadata = {
                "video_id": video_id,
                "url": f"https://youtube.com/shorts/{video_id}",
                "script": script,
                "duration": result["duration"],
                "clips_used": len(clips),
                "uploaded_at": datetime.now().isoformat()
            }
            with open(self.work_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"\n{'='*50}")
            print(f"SUCCESS: {video_id}")
            print(f"URL: https://youtube.com/shorts/{video_id}")
            print(f"{'='*50}")
            return True

        except Exception as e:
            print(f"\n{'='*50}")
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self._cleanup_old_runs()

    def _build_narration(self, script: Dict) -> str:
        niche = script.get("niche", "")

        if niche == "ai_tools":
            parts = [script.get("hook", "")]
            for step in script.get("steps", []):
                parts.append(step.get("narration", ""))
            parts.append(script.get("cta", ""))

        elif niche == "psychology":
            parts = [
                script.get("hook", ""),
                script.get("explanation", {}).get("what_it_is", ""),
                script.get("explanation", {}).get("real_example", ""),
                script.get("explanation", {}).get("why_it_matters", ""),
                script.get("practical_tip", ""),
                script.get("cta", "")
            ]

        else:
            parts = [script.get("cta", "")]

        parts = [p for p in parts if p]
        return " ".join(parts)

    def _cleanup_old_runs(self):
        base = Path("work")
        if not base.exists():
            return
        dirs = sorted([d for d in base.iterdir() if d.is_dir() and d.name.startswith(self.niche)])
        for d in dirs[:-5]:
            shutil.rmtree(d, ignore_errors=True)


async def run_niche(niche: str) -> bool:
    pipeline = Pipeline(niche)
    return await pipeline.run()