"""Import Kaggle notebooks/dataset/model outputs into project structure.

Usage example:
python scripts/import_kaggle_assets.py \
  --dataset-nb C:/path/01_synth_dataset.ipynb \
  --training-nb C:/path/02_train_yolo11m.ipynb \
  --logic-nb C:/path/03_checkout_logic.ipynb \
  --dataset-dir C:/path/exported_dataset \
  --dataset-version synthetic_v1 \
  --best-pt C:/path/runs/detect/train/weights/best.pt \
  --model-version v1
"""

from __future__ import annotations

import argparse
import json
import pickle
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _validate_file(path: str | None, label: str) -> Path | None:
    if not path:
        return None
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"{label} file not found: {p}")
    return p


def _validate_dir(path: str | None, label: str) -> Path | None:
    if not path:
        return None
    p = Path(path).expanduser().resolve()
    if not p.is_dir():
        raise NotADirectoryError(f"{label} directory not found: {p}")
    return p


def _write_model_metadata(model_dir: Path, model_version: str) -> Path:
    model_meta = {
        "model_version": model_version,
        "artifact": "best.pt",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    pkl_path = model_dir / "model_meta.pkl"
    with pkl_path.open("wb") as f:
        pickle.dump(model_meta, f)

    json_path = model_dir / "model_meta.json"
    json_path.write_text(json.dumps(model_meta, indent=2), encoding="utf-8")
    return pkl_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Kaggle project artifacts")
    parser.add_argument("--dataset-nb", help="Path to synthetic dataset notebook (.ipynb)")
    parser.add_argument("--training-nb", help="Path to YOLO training notebook (.ipynb)")
    parser.add_argument("--logic-nb", help="Path to checkout logic notebook (.ipynb)")
    parser.add_argument("--dataset-dir", help="Path to exported dataset directory")
    parser.add_argument("--dataset-version", default="synthetic_v1", help="Dataset version name")
    parser.add_argument("--best-pt", help="Path to trained best.pt file")
    parser.add_argument("--model-version", default="v1", help="Model version name")
    args = parser.parse_args()

    dataset_nb = _validate_file(args.dataset_nb, "dataset notebook")
    training_nb = _validate_file(args.training_nb, "training notebook")
    logic_nb = _validate_file(args.logic_nb, "checkout logic notebook")
    dataset_dir = _validate_dir(args.dataset_dir, "dataset")
    best_pt = _validate_file(args.best_pt, "best.pt")

    if dataset_nb:
        _copy_file(dataset_nb, ROOT / "notebooks" / "dataset" / "01_synthetic_dataset.ipynb")
    if training_nb:
        _copy_file(training_nb, ROOT / "notebooks" / "training" / "02_train_yolo11m.ipynb")
    if logic_nb:
        _copy_file(logic_nb, ROOT / "notebooks" / "checkout-logic" / "03_checkout_logic.ipynb")

    if dataset_dir:
        _copy_tree(dataset_dir, ROOT / "artifacts" / "datasets" / args.dataset_version)

    if best_pt:
        model_dir = ROOT / "artifacts" / "models" / args.model_version
        _copy_file(best_pt, model_dir / "best.pt")
        meta_path = _write_model_metadata(model_dir, args.model_version)
        print(f"Created metadata: {meta_path}")

    print("Import complete.")


if __name__ == "__main__":
    main()
