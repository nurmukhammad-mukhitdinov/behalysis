import base64
import uuid
from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings


def validate_and_decode_base64(data: str) -> bytes:
    """Validate a base64 string and return decoded bytes.

    Raises:
        HTTPException 422 if the string is not valid base64.
        HTTPException 413 if decoded size exceeds MAX_IMAGE_SIZE_BYTES.
    """
    # Strip optional data-URI prefix  (e.g. "data:image/jpeg;base64,...")
    if "," in data[:80]:
        data = data.split(",", 1)[1]

    try:
        decoded = base64.b64decode(data, validate=True)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid base64 image data")

    if len(decoded) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Image exceeds maximum allowed size of "
                f"{settings.MAX_IMAGE_SIZE_BYTES // 1024}KB"
            ),
        )
    return decoded


def save_image(image_b64: str, report_dir: Path) -> str:
    """Decode base64, save to disk, return relative filename."""
    decoded = validate_and_decode_base64(image_b64)

    # Detect simple format from magic bytes
    ext = _detect_extension(decoded)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = report_dir / filename
    filepath.write_bytes(decoded)
    return filename


def get_report_image_dir(report_id: str | uuid.UUID) -> Path:
    """Return (and create) the image directory for a given report."""
    report_dir = settings.IMAGES_DIR / str(report_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def _detect_extension(data: bytes) -> str:
    """Best-effort image format detection via magic bytes."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[:3] == b"GIF":
        return ".gif"
    # Default
    return ".bin"
