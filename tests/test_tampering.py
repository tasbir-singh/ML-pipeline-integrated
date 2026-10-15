import json
from pathlib import Path
from src.hashing import sha256_file
from src.verify import verify_manifest


def test_modified_file_is_detected(tmp_path: Path):
    tracked = tmp_path / "src" / "train.py"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("original", encoding="utf-8")
    manifest = {"files": [{"path": "src/train.py", "sha256": sha256_file(tracked)}]}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    tracked.write_text("modified", encoding="utf-8")
    report = verify_manifest(tmp_path, manifest_path)
    assert report["valid"] is False
    assert report["modified"] == ["src/train.py"]


def test_missing_file_is_detected(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"files": [{"path": "artifacts/model.pt", "sha256": "0" * 64}]}), encoding="utf-8")
    report = verify_manifest(tmp_path, manifest_path)
    assert report["valid"] is False
    assert report["missing"] == ["artifacts/model.pt"]
