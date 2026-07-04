"""ffmpeg audio post-processing."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "ffmpeg failed")


def audio_duration_ms(path: Path) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0
    try:
        return int(float(result.stdout.strip()) * 1000)
    except ValueError:
        return 0


def normalize_loudness(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "ffmpeg-normalize",
            str(input_path),
            "-o",
            str(output_path),
            "-f",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "24000",
        ]
    )


def concat_wavs(paths: list[Path], output_path: Path) -> None:
    if not paths:
        raise ValueError("No audio files to concat")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        list_path = Path(f.name)
        for p in paths:
            f.write(f"file '{p.resolve()}'\n")
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(output_path),
        ]
    )
    list_path.unlink(missing_ok=True)


def encode_export(
    chapter_files: list[tuple[str, Path]],
    output_path: Path,
    cover_path: Path | None = None,
    fmt: str = "m4b",
) -> None:
    """Encode concatenated chapters to m4b or mp3 with optional cover."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        list_path = Path(f.name)
        for _, p in chapter_files:
            f.write(f"file '{p.resolve()}'\n")

    temp_audio = output_path.with_suffix(".tmp.wav")
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c:a",
            "pcm_s16le",
            str(temp_audio),
        ]
    )
    list_path.unlink(missing_ok=True)

    codec = "aac" if fmt == "m4b" else "libmp3lame"
    ext = ".m4b" if fmt == "m4b" else ".mp3"
    if output_path.suffix != ext:
        output_path = output_path.with_suffix(ext)

    cmd = ["ffmpeg", "-y", "-i", str(temp_audio)]
    if cover_path and cover_path.exists():
        cmd += ["-i", str(cover_path), "-map", "0:a", "-map", "1:v", "-c:v", "mjpeg", "-disposition:v:0", "attached_pic"]
    cmd += ["-c:a", codec, "-b:a", "128k", str(output_path)]
    _run(cmd)
    temp_audio.unlink(missing_ok=True)
