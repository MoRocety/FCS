"""Decode uploads and store only normalized media, never user-controlled paths."""

import io
import re
import secrets
import subprocess
import tempfile
from pathlib import Path
from threading import BoundedSemaphore
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
import imageio_ffmpeg

IMAGE_LIMIT = 8 * 1024 * 1024
VIDEO_LIMIT = 20 * 1024 * 1024
MAX_PIXELS = 24_000_000
VIDEO_SLOTS = BoundedSemaphore(2)


def normalize(raw, root, description):
    """Return storage metadata. Remove partial output on all failure paths."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    name = secrets.token_hex(24)
    output = root / f"{name}.webp"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as source:
                if source.format not in ("JPEG", "PNG", "WEBP"):
                    raise ValueError("Use JPEG, PNG, WebP, MP4, or WebM media")
                if len(raw) > IMAGE_LIMIT:
                    raise ValueError("Each photo must be 8 MB or smaller")
                if source.width * source.height > MAX_PIXELS:
                    raise ValueError("Photos must contain fewer than 24 million pixels")
                if getattr(source, "is_animated", False):
                    raise ValueError(
                        "Use a still photo or a video clip, rather than animated images"
                    )
                source.load()
                image = ImageOps.exif_transpose(source)
                image.thumbnail((2048, 2048))
                # Rebuild from pixels so EXIF, XMP, ICC and text metadata cannot survive.
                pixels = image.convert("RGBA" if "A" in image.getbands() else "RGB")
                clean = Image.frombytes(pixels.mode, pixels.size, pixels.tobytes())
                clean.save(output, "WEBP", quality=85)
                output.chmod(0o600)
                return dict(
                    filename=output.name,
                    kind="image",
                    mime="image/webp",
                    width=clean.width,
                    height=clean.height,
                    duration=None,
                    bytes=output.stat().st_size,
                    description=description,
                )
    except UnidentifiedImageError:
        return normalize_video(raw, root, name, description)
    except (
        Image.DecompressionBombWarning,
        Image.DecompressionBombError,
        OSError,
    ) as exc:
        output.unlink(missing_ok=True)
        raise ValueError("This photo could not be decoded safely") from exc
    except Exception:
        output.unlink(missing_ok=True)
        raise


def run_video(args, timeout):
    try:
        result = subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-hide_banner", *args],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, RuntimeError) as exc:
        raise ValueError(
            "Video processing is unavailable on this server; try a photo"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            "This clip took too long to process; try a smaller clip"
        ) from exc
    if result.returncode:
        raise ValueError("This clip could not be decoded; use a valid MP4 or WebM file")
    return result.stderr.decode("utf-8", errors="replace")


def normalize_video(raw, root, name, description):
    if raw[4:8] == b"ftyp":
        format_args = ["-f", "mov", "-enable_drefs", "0", "-use_absolute_path", "0"]
    elif raw[:4] == b"\x1aE\xdf\xa3":
        format_args = ["-f", "matroska"]
    else:
        raise ValueError("Use JPEG, PNG, WebP, MP4, or WebM media")
    if len(raw) > VIDEO_LIMIT:
        raise ValueError("Clips must be 20 MB or smaller")
    if not VIDEO_SLOTS.acquire(blocking=False):
        raise ValueError("Video processing is busy; try again shortly")
    output = root / f"{name}.mp4"
    try:
        with tempfile.NamedTemporaryFile(dir=root, suffix=".upload") as source:
            source.write(raw)
            source.flush()
            # Restrict demuxers and protocols; do not follow playlists or movie references.
            inputs = [
                "-protocol_whitelist",
                "file,pipe",
                *format_args,
                "-i",
                source.name,
            ]
            info = run_video(
                [
                    *inputs,
                    "-map",
                    "0:v:0",
                    "-c:v",
                    "copy",
                    "-frames:v",
                    "1",
                    "-f",
                    "null",
                    "-",
                ],
                15,
            )
            duration = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", info)
            dimensions = re.search(r"Video: [^\n]*?\b(\d{2,5})x(\d{2,5})\b", info)
            if not duration or not dimensions:
                raise ValueError(
                    "The clip must have a readable duration and video track"
                )
            h, m, s = map(float, duration.groups())
            seconds = h * 3600 + m * 60 + s
            width, height = map(int, dimensions.groups())
            if not 0 < seconds <= 60:
                raise ValueError("Clips must be one minute or shorter")
            if width * height > MAX_PIXELS:
                raise ValueError("This clip's resolution is too large")
            run_video(
                [
                    "-y",
                    *inputs,
                    "-map",
                    "0:v:0",
                    "-map",
                    "0:a:0?",
                    "-t",
                    "60",
                    "-vf",
                    "scale=w='min(1280,iw)':h='min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "26",
                    "-pix_fmt",
                    "yuv420p",
                    "-threads",
                    "2",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "96k",
                    "-map_metadata",
                    "-1",
                    "-map_chapters",
                    "-1",
                    "-movflags",
                    "+faststart",
                    str(output),
                ],
                60,
            )
            if output.stat().st_size > VIDEO_LIMIT:
                raise ValueError("The processed clip exceeds 20 MB; try a smaller clip")
            output.chmod(0o600)
            return dict(
                filename=output.name,
                kind="video",
                mime="video/mp4",
                width=None,
                height=None,
                duration=seconds,
                bytes=output.stat().st_size,
                description=description,
            )
    except Exception:
        output.unlink(missing_ok=True)
        raise
    finally:
        VIDEO_SLOTS.release()
