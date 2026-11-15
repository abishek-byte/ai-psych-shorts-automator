"""Thumbnail generator using Pillow (no external API)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random
from pathlib import Path
from typing import Optional
from src.config import CONFIG

class ThumbnailMaker:
    def __init__(self):
        self.width = CONFIG.thumbnail_width
        self.height = CONFIG.thumbnail_height
        self.title_font_size = CONFIG.title_font_size
        self.subtitle_font_size = CONFIG.subtitle_font_size
        self.style = CONFIG.background_style

    def create(self, script: Dict, output_path: str, background_image: str = None) -> bool:
        try:
            if self.style == "gradient":
                img = self._create_gradient_bg(script.get("niche", "ai_tools"))
            elif self.style == "footage" and background_image and os.path.exists(background_image):
                img = self._create_footage_bg(background_image)
            else:
                img = self._create_solid_bg(script.get("niche", "ai_tools"))

            draw = ImageDraw.Draw(img)

            title_font = self._get_font(self.title_font_size, bold=True)
            subtitle_font = self._get_font(self.subtitle_font_size, bold=False)

            title_text = script.get("thumbnail_text", script.get("title", "AI Tools Daily"))[:40]
            self._draw_text_with_stroke(draw, title_text, title_font,
                                       position="center", y_offset=-60)

            subtitle_text = ""
            if script.get("niche") == "ai_tools":
                subtitle_text = script.get("tool", {}).get("name", "")[:30]
            elif script.get("niche") == "psychology":
                subtitle_text = script.get("topic_data", {}).get("topic", "")[:30]

            if subtitle_text:
                self._draw_text_with_stroke(draw, subtitle_text, subtitle_font,
                                           position="center", y_offset=60,
                                           fill="#FFD700", stroke_fill="#000000")

            niche = script.get("niche", "ai_tools")
            badge_text = "AI TOOLS" if niche == "ai_tools" else "PSYCHOLOGY"
            badge_font = self._get_font(36, bold=True)
            self._draw_text_with_stroke(draw, badge_text, badge_font,
                                       position="bottom", y_offset=-40,
                                       fill="#FFFFFF", stroke_fill="#000000")

            img.save(output_path, "JPEG", quality=95)
            print(f"Thumbnail saved: {output_path}")
            return True

        except Exception as e:
            print(f"Thumbnail error: {e}")
            return False

    def _create_gradient_bg(self, niche: str) -> Image.Image:
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)

        if niche == "ai_tools":
            colors = [(0x0F, 0x17, 0x2A), (0x1E, 0x1E, 0x3F), (0x3B, 0x00, 0x6E)]
        else:
            colors = [(0x1A, 0x1A, 0x2E), (0x2D, 0x1B, 0x3D), (0x6A, 0x0D, 0x4D)]

        for y in range(self.height):
            ratio = y / self.height
            if ratio < 0.5:
                c1, c2 = colors[0], colors[1]
                t = ratio * 2
            else:
                c1, c2 = colors[1], colors[2]
                t = (ratio - 0.5) * 2

            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        noise = Image.effect_noise((self.width, self.height), 100).convert("L")
        img = Image.composite(img, Image.new("RGB", img.size, (0,0,0)), noise.point(lambda x: x * 0.05))

        return img

    def _create_solid_bg(self, niche: str) -> Image.Image:
        if niche == "ai_tools":
            color = (0x0F, 0x17, 0x2A)
        else:
            color = (0x1A, 0x1A, 0x2E)
        return Image.new("RGB", (self.width, self.height), color)

    def _create_footage_bg(self, image_path: str) -> Image.Image:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")

        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        return img

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    pass

        return ImageFont.load_default()

    def _draw_text_with_stroke(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                               position: str, y_offset: int, fill: str = "#FFFFFF",
                               stroke_fill: str = "#000000", stroke_width: int = 4):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2 + y_offset

        for dx in [-stroke_width, 0, stroke_width]:
            for dy in [-stroke_width, 0, stroke_width]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)

        draw.text((x, y), text, font=font, fill=fill)

def make_thumbnail(script: Dict, output_path: str, background_image: str = None) -> bool:
    maker = ThumbnailMaker()
    return maker.create(script, output_path, background_image)