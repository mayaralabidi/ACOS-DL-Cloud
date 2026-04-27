"""Lightweight per-class spatial cluster tracker."""

from __future__ import annotations


def _centroid(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


class ClusterTracker:
    """
    Groups same-class detections by centroid proximity across frames (optional).

    Used by StaticSceneCheckout when use_spatial_tracking=True to track individual
    objects across consecutive frames. This provides:

    - **Cluster stability:** Objects that move slightly between frames keep the same ID
    - **EMA smoothing:** Cluster centroids use exponential moving average for stability
    - **Timeout handling:** Clusters that disappear for max_lost frames are pruned

    **Usage:**
        tracker = ClusterTracker(dist_threshold=80.0, ema_alpha=0.5, max_lost=10)
        for frame in video:
            detections = [...get from YOLO...]
            tracked = tracker.update(detections)  # Returns (cluster_id, box) tuples

    **Note:** This is optional. The main confirmation system uses temporal frame-hit
    accumulation (class_conf_history) regardless of spatial tracking.
    """

    def __init__(
        self,
        dist_threshold: float = 80.0,
        ema_alpha: float = 0.5,
        max_lost: int = 10,
    ) -> None:
        """
        Initialize cluster tracker.

        Args:
            dist_threshold: Max centroid distance to match cluster (pixels)
            ema_alpha: EMA weight for centroid smoothing (0.5 = equal weight old/new)
            max_lost: Frames to keep unmatched cluster before pruning
        """
        self._clusters: dict[int, dict] = {}
        self._next_id = 0
        self.dist_threshold = dist_threshold
        self.ema_alpha = ema_alpha
        self.max_lost = max_lost

    def update(self, boxes: list[list]) -> list[tuple[int, list]]:
        """
        Match boxes to existing clusters and return tracked detections.

        Boxes that move less than dist_threshold pixels are matched to existing clusters.
        New boxes create new clusters. Unmatched clusters increment lost counter.

        Args:
            boxes: List of [x1, y1, x2, y2] bounding boxes

        Returns:
            List of (cluster_id, box) tuples matching input boxes
        """
        for c in self._clusters.values():
            c["lost"] += 1

        result: list[tuple[int, list]] = []
        for box in boxes:
            cx, cy = _centroid(box)
            best_id, best_dist = None, float("inf")
            for cid, c in self._clusters.items():
                d = _dist((cx, cy), c["centre"])
                if d < best_dist:
                    best_dist = d
                    best_id = cid

            if best_id is not None and best_dist < self.dist_threshold:
                ocx, ocy = self._clusters[best_id]["centre"]
                self._clusters[best_id]["centre"] = (
                    self.ema_alpha * cx + (1 - self.ema_alpha) * ocx,
                    self.ema_alpha * cy + (1 - self.ema_alpha) * ocy,
                )
                self._clusters[best_id]["hits"] += 1
                self._clusters[best_id]["lost"] = 0
                result.append((best_id, box))
            else:
                cid = self._next_id
                self._next_id += 1
                self._clusters[cid] = {
                    "centre": (cx, cy),
                    "hits": 1,
                    "lost": 0,
                }
                result.append((cid, box))

        self._clusters = {
            cid: c for cid, c in self._clusters.items() if c["lost"] <= self.max_lost
        }
        return result

    def confirmed_count(self, min_hits: int) -> int:
        """Return number of clusters with hits >= min_hits (i.e., confirmed objects)."""
        return sum(1 for c in self._clusters.values() if c["hits"] >= min_hits)

    def any_confirmed(self, min_hits: int) -> bool:
        """Return True if any cluster has hits >= min_hits (i.e., any object confirmed)."""
        return self.confirmed_count(min_hits) > 0

    @property
    def clusters(self) -> dict[int, dict]:
        """Read-only cluster state."""
        return self._clusters
