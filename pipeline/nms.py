"""Cross-class Non-Maximum Suppression helpers."""

from __future__ import annotations


# Product families that should use stricter NMS (family_iou_threshold).
# Within-family confusion is more likely (similar appearance, packaging),
# so we apply stricter suppression to avoid missing one product when two overlap.
# Example: dryyeast_smartchef partially misidentified as vanillinatedsugar.
SAME_FAMILY_GROUPS: list[set[str]] = [
    {"soapbar_dove_shea", "soapbar_dove_lavender"},
    {"shampoo_elseve_hya", "shampoo_elseve_gly", "shampoo_elvive"},
    {"butter_jadida", "butter_delice"},
    {"dryyeast_smartchef", "dryyeast_lapatissiere"},
    {"yogurt_danette", "yogurt_delice"},
    {"pasta_spaghetti", "pasta_fell", "pasta_canelloni"},
]


def _iou(a: list[float], b: list[float]) -> float:
    """Intersection over Union for two boxes [x1,y1,x2,y2]."""
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter == 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter + 1e-6)


def _same_family(label_a: str, label_b: str) -> bool:
    """Check if two product labels belong to the same family group."""
    return any(label_a in g and label_b in g for g in SAME_FAMILY_GROUPS)


def cross_class_nms(
    detections: list[list],
    default_iou_threshold: float = 0.20,
    family_iou_threshold: float = 0.10,
    model_names: dict[int, str] | None = None,
) -> list[list]:
    """
    Suppress overlapping boxes across ALL classes (not just same-class).

    Standard YOLO NMS only suppresses within the same class. This function also
    handles different-class overlaps — catching cases where the model fires
    two labels on the same physical object (e.g. dryyeast partially misidentified
    as vanillinatedsugar).

    **Why different thresholds?**
    - `default_iou_threshold`: Suppress different-class overlaps (~0.20-0.40 depending on resolution)
    - `family_iou_threshold`: Stricter for same-family products (~0.10) since they're easy to confuse

    At 1920×1080, large product boxes naturally share 20–40% overlap from being
    placed close together. A threshold of 0.20 suppresses 37–60% of valid detections.
    At 0.40, only boxes that genuinely cover the same object are removed.

    Args:
        detections: List of [x1, y1, x2, y2, conf, cls] boxes
        default_iou_threshold: IoU threshold for different-class suppression
        family_iou_threshold: Stricter threshold for same-family products
        model_names: Dict mapping class index to label string

    Returns:
        Filtered detections sorted by confidence (highest first)
    """
    if not detections:
        return []
    names = model_names or {}
    dets = sorted(detections, key=lambda d: d[4], reverse=True)
    kept: list[list] = []
    while dets:
        best = dets.pop(0)
        kept.append(best)
        label_best = names.get(int(best[5]), "")
        remaining = []
        for d in dets:
            label_d = names.get(int(d[5]), "")
            threshold = (
                family_iou_threshold
                if _same_family(label_best, label_d)
                else default_iou_threshold
            )
            if _iou(best[:4], d[:4]) < threshold:
                remaining.append(d)
        dets = remaining
    return kept
