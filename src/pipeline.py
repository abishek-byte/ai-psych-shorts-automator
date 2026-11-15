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
from src.niches.psychotor

class Pipeline:
    def __init__(self, niche: str):
        self.niche = n
        self.llm = LLMClient()
        self.tts = TTS
        self.footage = FootageFetcher()
        self.work_dirPath(f"work/{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.work_dir.=True)

        if niche == "a
            self.generator = AIToolsGenerator(self.llm)
            self.stylels",{}).get("prompt_style", "tutorial")
        elif niche ==
            self.generator = PsychologyGenerator(self.llm)
            self.stylelogy",{}).get("prompt_style", "fact")
        else:
            raise ValueError(f"Unknown niche: {niche}")

    async def run(self) -> bool:
        print(f"\n{'='
        print(f"Starting {self.niche} pipeline")
        print(f"{'='*5


            print("1. Generating script...")
            script = s(self.style)
            script_path = self.work_dir / "script.json"
            with open(
                json.dump(script, f, indent=2)
            print(f"   'Untitled')}")

            print("2.
            narration_text = self._build_narration(script)
            audio_path.wav"
            srt_path = self.work_dir / "narration.srt"

            result = await self.tts.synthesize(narration_text,
str(audio_path))
            self.tts.create_srt(result["word_timestamps"], str(srt_path))
            print(f"  ]:.1f}s")

            print("3.
            clips = self.footage.fetch_for_script(script, self.work_dir /
"clips")
            print(f"   Got {len(clips)} clips")

            print("4. Assembling video...")
            video_path"

            bgm_path =
            if CONFIG.bgm_tracks:
                for tr
                    if os.path.exists(track):

                        break

            success = create_vertical_video(
                clips,h),
                str(video_path), bgm_path
            )
            if not success:
                raise failed")

            print("5.
            thumb_path = self.work_dir / "thumbnail.jpg"
            bg_frame =
            make_thumbnail(script, str(thumb_path), bg_frame)

            print("6. Uploading to YouTube...")
            video_id =, str(thumb_path),script)
            if not vid
                raise RuntimeError("Upload failed")

            metadata = {
                "video
                "url": f"https://youtube.com/shorts/{video_id}",
                "scrip
                "duration": result["duration"],
                "clips
                "uploaded_at": datetime.now().isoformat()
            }
            with open(self.work_dir / "metadata.json", "w") as f:
                json.d

            print(f"\n
            return True

        except Exception as e:
            print(f"\n
            import traceback
            traceback.
            return False

        finally:
            self._clea

    def _build_narrati:
        niche = script.get("niche", "")

        if niche == "ai_tools":
            parts = [s
            for step in script.get("steps", []):
                parts.""))
            parts.append(script.get("cta", ""))

        elif niche == "psychology":
            parts = [
                script.get("hook", ""),
                scriptwhat_it_is", ""),
                script.get("explanation", {}).get("real_example", ""),
                scriptwhy_it_matters", ""),
                script.get("practical_tip", ""),
                script
            ]

        else:
            parts = [s.get("cta", "")]

        parts = [p for)]
        return " ".join(parts)

    def _cleanup_old_runs(self):
        base = Path("w
        dirs = sorted([d for d in base.iterdir() if d.is_dir() and
d.name.startswith(self
        for d in dirs[:-5]:
            shutil.rmt

async def run_niche(ni
    pipeline = Pipeline(niche)
    return await pipel