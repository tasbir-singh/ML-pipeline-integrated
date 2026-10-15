# ML Pipeline Integrity Auditor

A small research-oriented prototype that records selected ML experiment artefacts in a JSON manifest, hashes file bytes with SHA-256, detects missing or modified files, and optionally signs the manifest with Ed25519.

## What it does and does not establish

- **Integrity check:** detects whether listed file bytes match the hashes in a manifest.
- **Authenticity (optional):** verifies whether a manifest signature matches a public key you trust.
- **Not established:** honest training, correct dataset origin, model quality, fairness, privacy, robustness, or safety.
- **Scope:** only the explicit paths in `src/inventory.py` are covered. This is a teaching/research prototype, not production security tooling.

## Requirements

Python 3.10+ is recommended. Create and activate a virtual environment in VS Code's terminal:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS/Linux
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can use `.venv\\Scripts\\python.exe -m pip install -r requirements.txt` and run commands with `.venv\\Scripts\\python.exe` without activating the environment.

## Run the experiment

```bash
python -m src.train
python -m src.manifest
python -m src.verify
python -m pytest -q
```

The `load_digits` dataset is bundled with scikit-learn, so the training step does not need to download a dataset. It trains a small multilayer perceptron and writes `artifacts/model.pt` and `artifacts/evaluation.json`.

## Demonstrate tamper detection

1. Run training and create the manifest as above.
2. Edit `configs/experiment.json` (for example, change `epochs` from 12 to 13).
3. Run `python -m src.verify` again. The configuration should be reported under `modified` and the command should exit with status 1.
4. Restore the original config and rerun `python -m src.manifest` to create a fresh reference manifest.

A manifest is a reference record. If an attacker can replace both files and an unsigned manifest, they can recalculate the hashes. Keep a trusted copy or sign the manifest.

## Optional Ed25519 manifest signature

The following commands create a key pair, sign the manifest, and verify it. Run from the project root:

```bash
python -m src.signing keygen --private keys/private.pem --public keys/public.pem
python -m src.signing sign --manifest artifacts/manifest.json --private keys/private.pem --signature artifacts/manifest.sig
python -m src.signing verify --manifest artifacts/manifest.json --public keys/public.pem --signature artifacts/manifest.sig
```

**Key-management caveat:** protect the private key and distribute the public key through a trusted channel. A public key stored beside a manifest is not automatically trusted. Do not commit private keys to version control. This demo writes an unencrypted private key for local experimentation; production use should use protected key storage and access controls.

To test signature detection, edit `artifacts/manifest.json` after signing and run the verify command. Verification should fail. Recreate and re-sign the manifest after restoring the file.

## Manifest coverage

Each manifest file entry contains a project-relative path, SHA-256 digest of the exact file bytes, and file size in bytes. The manifest does not hash itself or its signature. `src/inventory.py` explicitly lists the covered files; add new important files there to include them in verification.

The dataset fingerprint in `artifacts/evaluation.json` is computed over the contiguous feature array bytes followed by the label array bytes for the bundled `load_digits` dataset. It is an identifier for those arrays, not proof of provenance or license.

## Research extension ideas

- Add a machine-readable threat model and a richer MLBOM schema.
- Record library versions and compare them against a lockfile.
- Separate provenance claims from integrity claims in the manifest.
- Benchmark verification runtime and manifest size.
- Investigate signed attestations produced by a trusted build environment.
- Explore verifiable evaluation claims, carefully distinguishing evidence that a test ran from proof that a model property holds.

See `reports/evaluation.md` for an evaluation template. Record only measurements you actually observe.
