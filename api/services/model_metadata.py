"""Helpers for reading local model metadata artifacts."""

from __future__ import annotations

import pickle
from pathlib import Path

from ..config import get_settings


def load_model_metadata(model_path: str | None = None) -> dict[str, str]:
    """Load metadata from model_meta.pkl when available.

    Search order:
    1) Same directory as model file (model_meta.pkl)
    2) artifacts/models/<MODEL_VERSION>/model_meta.pkl
    3) fallback to env model_version
    """
    settings = get_settings()

    candidates: list[Path] = []
    if model_path:
        model_file = Path(model_path)
        # For aliases like "yolo11m.pt", Path.parent == '.' and lookup is harmless.
        candidates.append(model_file.parent / "model_meta.pkl")

    candidates.append(Path("artifacts") / "models" / settings.model_version / "model_meta.pkl")

    for candidate in candidates:
        if not candidate.exists():
            continue

        try:
            with candidate.open("rb") as f:
                value = pickle.load(f)
            if isinstance(value, dict):
                model_version = str(value.get("model_version") or settings.model_version)
                return {"model_version": model_version}
        except Exception:
            continue

    return {"model_version": settings.model_version}
