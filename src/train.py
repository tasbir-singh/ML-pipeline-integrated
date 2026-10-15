"""Train a small PyTorch classifier on scikit-learn's bundled digits dataset."""
from __future__ import annotations
import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.hashing import sha256_bytes


class DigitsMLP(nn.Module):
    def __init__(self, hidden_units: int = 64) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(64, hidden_units), nn.ReLU(), nn.Linear(hidden_units, 10)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


def train(root: Path = ROOT) -> dict:
    config = json.loads((root / "configs/experiment.json").read_text(encoding="utf-8"))
    seed = int(config["random_seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)

    digits = load_digits()
    # Fingerprint the exact bundled feature and label arrays used by this run.
    dataset_bytes = np.ascontiguousarray(digits.data, dtype=np.float64).tobytes() + np.ascontiguousarray(digits.target, dtype=np.int64).tobytes()
    dataset_fingerprint = sha256_bytes(dataset_bytes)
    x_train, x_test, y_train, y_test = train_test_split(
        digits.data, digits.target, test_size=float(config["test_size"]),
        random_state=seed, stratify=digits.target
    )
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train).astype(np.float32)
    x_test = scaler.transform(x_test).astype(np.float32)
    train_ds = TensorDataset(torch.from_numpy(x_train), torch.tensor(y_train, dtype=torch.long))
    generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(train_ds, batch_size=int(config["batch_size"]), shuffle=True, generator=generator)

    model = DigitsMLP(int(config["hidden_units"]))
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["learning_rate"]))
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(int(config["epochs"])):
        for features, labels in loader:
            optimizer.zero_grad()
            loss = criterion(model(features), labels)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(x_test))
        predictions = logits.argmax(dim=1).numpy()
    accuracy = float(np.mean(predictions == y_test))

    artifacts = root / "artifacts"
    artifacts.mkdir(exist_ok=True)
    # Save weights and the preprocessing parameters needed to interpret inputs.
    torch.save({
        "model_state_dict": model.state_dict(),
        "scaler_mean": torch.tensor(scaler.mean_, dtype=torch.float64),
        "scaler_scale": torch.tensor(scaler.scale_, dtype=torch.float64),
        "hidden_units": int(config["hidden_units"]),
        "class_count": 10,
    }, artifacts / "model.pt")
    result = {
        "experiment_name": config["experiment_name"],
        "dataset": config["dataset"],
        "dataset_fingerprint_sha256": dataset_fingerprint,
        "dataset_rows": int(len(digits.data)),
        "feature_count": int(digits.data.shape[1]),
        "random_seed": seed,
        "test_size": float(config["test_size"]),
        "epochs": int(config["epochs"]),
        "test_accuracy": accuracy,
        "note": "Accuracy is a baseline metric, not a security, privacy, fairness, or robustness guarantee."
    }
    (artifacts / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root directory")
    args = parser.parse_args()
    train(args.root.resolve())
