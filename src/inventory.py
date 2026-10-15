"""Define the intentionally small set of files tracked by the manifest."""
from pathlib import Path

# Paths are relative to the project root. The manifest and signature are excluded
# to avoid self-referential hashing and signature recursion.
TRACKED_PATHS = (
    "README.md",
    "requirements.txt",
    "configs/experiment.json",
    "src/hashing.py",
    "src/train.py",
    "src/inventory.py",
    "src/manifest.py",
    "src/verify.py",
    "src/signing.py",
    "artifacts/model.pt",
    "artifacts/evaluation.json",
)


def tracked_paths(root: Path) -> list[Path]:
    return [root / rel for rel in TRACKED_PATHS]
