from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """All hyperparameters for the checkout pipeline."""

    model_path: str
    multi_instance: bool = False
    conf_threshold: float = 0.40
    detection_floor: float = 0.20  # Must stay below all class_conf_overrides to allow filtering
    min_confirm_frames: int = 6
    nms_iou_threshold: float = 0.40  # Calibrated for 1920x1080 (see notebook section 4 for rationale)
    nms_family_iou_threshold: float = 0.10  # Stricter suppression for product families (soaps, shampoos, butters, etc)
    max_box_ratio: float = 0.92  # Filter boxes larger than 92% of frame (catches image corruption)
    cluster_dist_threshold: float = 80.0  # Spatial tracking: max distance to merge clusters (pixels)
    cluster_ema_alpha: float = 0.5  # Spatial tracking: centroid EMA weight (0.5 = equal old/new)
    cluster_max_lost: int = 10  # Spatial tracking: frames to keep unmatched cluster before pruning
    frame_skip: int = 2  # Default=2 for speed-first processing; set to 1 for maximum accuracy
    use_spatial_tracking: bool = False  # Enable ClusterTracker for frame-to-frame object tracking
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