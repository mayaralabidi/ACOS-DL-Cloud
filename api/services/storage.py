"""GCS helpers: download model weights, upload/download video files."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _is_ultralytics_identifier(model_path: str) -> bool:
    """Return True when model_path looks like an Ultralytics model alias."""
    normalized = model_path.replace("\\", "/")
    return "/" not in normalized and normalized.endswith(".pt")


def download_model_if_needed() -> str:
    """Ensure model availability and return the model path/identifier to load."""
    from ..config import get_settings

    settings = get_settings()
    local_path = Path(settings.model_local_path)
    if local_path.exists():
        logger.info("Model weights found at %s", local_path)
        return settings.model_local_path

    # Local-dev fallback: auto-discover project artifacts model weights.
    discovered_models = sorted(Path("artifacts/models").glob("*/best.pt"))
    if discovered_models:
        selected = discovered_models[0]
        logger.info(
            "Configured model %s not found; using discovered local model %s",
            local_path,
            selected,
        )
        return str(selected)

    if not settings.gcs_bucket_name:
        if _is_ultralytics_identifier(settings.model_local_path):
            logger.warning(
                "Model file %s not found and no GCS bucket configured; "
                "falling back to Ultralytics auto-download for '%s'.",
                local_path,
                settings.model_local_path,
            )
            return settings.model_local_path

        fallback_model = "yolov8n.pt"
        logger.warning(
            "Model file %s not found and no GCS bucket configured; "
            "using local-dev fallback model '%s'.",
            local_path,
            fallback_model,
        )
        return fallback_model

    logger.info(
        "Downloading model from gs://%s/%s",
        settings.gcs_bucket_name,
        settings.gcs_model_path,
    )
    from google.cloud import storage

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        client = storage.Client(project=settings.gcp_project_id)
        bucket = client.bucket(settings.gcs_bucket_name)
        blob = bucket.blob(settings.gcs_model_path)
        blob.download_to_filename(str(local_path))
        logger.info("Model downloaded to %s", local_path)
        return settings.model_local_path
    except Exception as exc:
        fallback_model = "yolov8n.pt"
        logger.warning(
            "GCS model download failed (%s). Using local-dev fallback model '%s'.",
            exc,
            fallback_model,
        )
        return fallback_model