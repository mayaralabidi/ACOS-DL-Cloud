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
    detection_floor: float = 0.20  # Must stay below all class_conf_overrides
    min_confirm_frames: int = 6
    nms_iou_threshold: float = 0.40  # Calibrated for 1920x1080; at 0.20 suppresses 37-60% valid detections
    nms_family_iou_threshold: float = 0.10  # Stricter for product families (e.g. soaps, shampoos)
    cluster_dist_threshold: float = 80.0
    cluster_ema_alpha: float = 0.5  # Spatial tracking: exponential moving average for centroid smoothing
    cluster_max_lost: int = 10  # Spatial tracking: frames to keep cluster before pruning
    frame_skip: int = 2  # Default=2 for speed-first processing; set to 1 for maximum accuracy
    multi_instance: bool = True
    use_spatial_tracking: bool = False
    verbose_output: bool = False

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