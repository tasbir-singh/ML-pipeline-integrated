from pathlib import Path
from src.hashing import sha256_bytes, sha256_file


def test_known_sha256_digest():
    assert sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_file_hash_matches_bytes(tmp_path: Path):
    file = tmp_path / "sample.bin"
    file.write_bytes(b"auditable ML")
    assert sha256_file(file) == sha256_bytes(b"auditable ML")
