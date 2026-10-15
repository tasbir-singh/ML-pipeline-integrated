# Evaluation report template

Fill this report after running the experiment and verification tests. Do not claim measurements you have not collected.

## Environment
- OS / Python version:
- CPU/GPU:
- PyTorch and scikit-learn versions:

## Baseline model
- Dataset: scikit-learn `load_digits` (bundled dataset; 8x8 handwritten digit features)
- Seed, epochs, split: see `configs/experiment.json`
- Test accuracy: copy from `artifacts/evaluation.json`

## Integrity experiments
| Scenario | Expected result | Observed result | Notes |
|---|---|---|---|
| Untouched tracked files | All manifest hashes match | | |
| Modified model checkpoint | `artifacts/model.pt` reported modified | | |
| Modified configuration | `configs/experiment.json` reported modified | | |
| Deleted tracked file | File reported missing | | |
| New unlisted tracked-path file | File reported unexpected | | |
| Edited manifest after signing | Signature verification fails | | |

## Metrics to collect
- Verification runtime (repeat and report median).
- Manifest size in bytes.
- Number of files and bytes covered by the manifest.
- Tampering detection coverage across tested scenarios.

## Threat model and limitations
- Hashes detect mismatches only against a trusted manifest.
- An unsigned manifest can be replaced together with the artefacts.
- A signature authenticates the signed manifest relative to a trusted public key; it does not prove the signer trained the model honestly.
- If an attacker controls the signing key or trusted build machine, signatures may not provide the expected assurance.
- Only files listed in `src/inventory.py` are in scope. This prototype is not a full recursive dependency or dataset supply-chain scanner.
- The dataset fingerprint identifies the feature/label arrays used here; it does not certify dataset origin or licensing.
- Model accuracy does not establish fairness, privacy, robustness, or safety.
