from pathlib import Path
from typing import Final
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


ALLOWED_EXTENSIONS: Final[set[str]] = {".pdf", ".txt", ".md"}


def ensure_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_upload_file(file: UploadFile) -> str:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Only PDF, TXT, and MD files are allowed.")
    return suffix


def build_storage_path(filename: str) -> Path:
    upload_dir = ensure_upload_dir()
    safe_name = Path(filename).name or "upload"
    return upload_dir / f"{uuid4()}_{safe_name}"


def validate_file_size(content: bytes) -> None:
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise ValueError(
            f"Uploaded file exceeds the {settings.MAX_UPLOAD_SIZE_BYTES} byte limit."
        )
