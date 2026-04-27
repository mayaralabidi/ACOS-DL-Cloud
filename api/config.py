from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_env: str = "dev"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    database_url: str

    gcp_project_id: str = ""
    gcs_bucket_name: str = ""
    gcs_model_path: str = "yolo11m/v1/best.pt"
    gcs_video_bucket: str = ""

    model_local_path: str = "/app/weights/best.pt"
    model_version: str = "v1"

    conf_threshold: float = 0.40
    detection_floor: float = 0.20
    min_confirm_frames: int = 6
    nms_iou_threshold: float = 0.20
    nms_family_iou_threshold: float = 0.10
    cluster_dist_threshold: float = 80.0
    cluster_ema_alpha: float = 0.5
    cluster_max_lost: int = 10
    frame_skip: int = 1
    multi_instance: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8001
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins from env into a list."""
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Return singleton settings instance."""
    return Settings()