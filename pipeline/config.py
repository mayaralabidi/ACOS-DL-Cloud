from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """All hyperparameters for the checkout pipeline."""

    model_path: str
    multi_instance: bool = False
    conf_threshold: float = 0.40
    detection_floor: float = 0.20
    min_confirm_frames: int = 6
    nms_iou_threshold: float = 0.20
    nms_family_iou_threshold: float = 0.10
    max_box_ratio: float = 0.92
    cluster_dist_threshold: float = 80.0
    cluster_ema_alpha: float = 0.5
    cluster_max_lost: int = 10
    frame_skip: int = 1
    class_conf_overrides: dict[str, float] = field(
        default_factory=lambda: {
            "soapbar_dove_shea": 0.25,
            "soapbar_dove_lavender": 0.25,
            "toothpaste_colgate": 0.30,
        }
    )
    min_frames_overrides: dict[str, int] = field(
        default_factory=lambda: {
            "soapbar_dove_shea": 3,
            "soapbar_dove_lavender": 3,
            "toothpaste_colgate": 3,
        }
    )
    qty_overrides: dict[str, int] = field(default_factory=dict)