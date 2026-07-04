"""Book cover extraction and placeholder generation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import COVERS_DIR


def save_cover_bytes(book_id: int, data: bytes, source: str = "extracted") -> str:
    path = COVERS_DIR / f"{book_id}.png"
    path.write_bytes(data)
    return str(path)


def generate_placeholder(title: str, book_id: int) -> str:
    size = 512
    img = Image.new("RGB", (size, size), color="#141417")
    draw = ImageDraw.Draw(img)
    initial = (title.strip()[:1] or "N").upper()
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 200)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initial, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 20), initial, fill="#d4a853", font=font)
    path = COVERS_DIR / f"{book_id}.png"
    img.save(path, "PNG")
    return str(path)


def save_custom_cover(book_id: int, image_path: Path) -> str:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((512, 512), Image.Resampling.LANCZOS)
    out = COVERS_DIR / f"{book_id}.png"
    img.save(out, "PNG")
    return str(out)
