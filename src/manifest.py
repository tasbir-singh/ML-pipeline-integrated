"""Create a JSON manifest containing SHA-256 hashes of tracked artefacts."""
from __future__ import annotations
import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.hashing import sha256_file
from src.inventory import tracked_paths


def create_manifest(root: Path = ROOT, output: Path | None = None) -> dict:
    root = root.resolve()
    files = []
    for path in tracked_paths(root):
        if not path.is_file():
            raise FileNotFoundError(f"Required tracked file is missing: {path.relative_to(root)}")
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "hash_algorithm": "SHA-256",
        "project": "ML Pipeline Integrity Auditor",
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "files": files,
        "scope_note": "Hashes cover only listed file bytes. They do not prove training honesty, model quality, or any safety/privacy/fairness property.",
    }
    target = output or (root / "artifacts/manifest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = create_manifest(args.root, args.output)
    print(f"Wrote manifest with {len(result['files'])} entries.")
