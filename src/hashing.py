"""File hashing helpers for the ML Pipeline Integrity Auditor."""
from __future__ import annotations
import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Return the lowercase SHA-256 hex digest of a file, streamed in chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()
