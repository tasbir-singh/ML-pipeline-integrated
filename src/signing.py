"""Optional Ed25519 signing for manifest authenticity."""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def generate_keypair(private_path: Path, public_path: Path) -> None:
    private_key = Ed25519PrivateKey.generate()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    public_path.write_bytes(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    try:
        private_path.chmod(0o600)
    except OSError:
        pass


def sign_manifest(manifest_path: Path, private_path: Path, signature_path: Path) -> None:
    private_key = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
    signature = private_key.sign(manifest_path.read_bytes())
    signature_path.write_text(base64.b64encode(signature).decode("ascii") + "\n", encoding="ascii")


def verify_signature(manifest_path: Path, public_path: Path, signature_path: Path) -> bool:
    public_key = serialization.load_pem_public_key(public_path.read_bytes())
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError("The provided public key is not Ed25519")
    signature = base64.b64decode(signature_path.read_text(encoding="ascii").strip(), validate=True)
    try:
        public_key.verify(signature, manifest_path.read_bytes())
        return True
    except Exception:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    keygen = sub.add_parser("keygen")
    keygen.add_argument("--private", type=Path, default=Path("keys/private.pem"))
    keygen.add_argument("--public", type=Path, default=Path("keys/public.pem"))
    sign = sub.add_parser("sign")
    sign.add_argument("--manifest", type=Path, default=Path("artifacts/manifest.json"))
    sign.add_argument("--private", type=Path, default=Path("keys/private.pem"))
    sign.add_argument("--signature", type=Path, default=Path("artifacts/manifest.sig"))
    check = sub.add_parser("verify")
    check.add_argument("--manifest", type=Path, default=Path("artifacts/manifest.json"))
    check.add_argument("--public", type=Path, default=Path("keys/public.pem"))
    check.add_argument("--signature", type=Path, default=Path("artifacts/manifest.sig"))
    args = parser.parse_args()
    if args.command == "keygen":
        generate_keypair(args.private, args.public)
        print(f"Created private key {args.private} and public key {args.public}")
    elif args.command == "sign":
        sign_manifest(args.manifest, args.private, args.signature)
        print(f"Signed {args.manifest} -> {args.signature}")
    else:
        valid = verify_signature(args.manifest, args.public, args.signature)
        print(json.dumps({"signature_valid": valid}, indent=2))
        raise SystemExit(0 if valid else 1)
