"""Verify file hashes, reporting missing, modified, and unexpected files."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.hashing import sha256_file
from src.inventory import TRACKED_PATHS


def verify_manifest(root: Path = ROOT, manifest_path: Path | None = None) -> dict:
    root = root.resolve()
    manifest_file = manifest_path or (root / "artifacts/manifest.json")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    entries = {entry["path"]: entry for entry in manifest.get("files", [])}
    expected_paths = set(entries)
    missing, modified, ok = [], [], []
    for rel, entry in entries.items():
        path = root / rel
        if not path.is_file():
            missing.append(rel)
        elif sha256_file(path) != entry["sha256"]:
            modified.append(rel)
        else:
            ok.append(rel)
    # Unexpected means a file in the declared tracked set exists but is not in
    # the manifest; untracked files elsewhere are intentionally outside scope.
    unexpected = sorted(rel for rel in TRACKED_PATHS if (root / rel).is_file() and rel not in expected_paths)
    return {"valid": not (missing or modified or unexpected), "verified": ok,
            "missing": missing, "modified": modified, "unexpected": unexpected,
            "manifest": str(manifest_file)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()
    result = verify_manifest(args.root, args.manifest)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)
