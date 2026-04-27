"""Lightweight per-class spatial cluster tracker."""

from __future__ import annotations


def _centroid(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


class ClusterTracker:
    """Groups same-class detections by centroid proximity across frames."""

    def __init__(
        self,
        dist_threshold: float = 80.0,
        ema_alpha: float = 0.5,
        max_lost: int = 10,
    ) -> None:
        self._clusters: dict[int, dict] = {}
        self._next_id = 0
        self.dist_threshold = dist_threshold
        self.ema_alpha = ema_alpha
        self.max_lost = max_lost

    def update(self, boxes: list[list]) -> list[tuple[int, list]]:
        """Match boxes to clusters. Returns (cluster_id, box) per box."""
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
        """Return number of clusters with hits >= min_hits."""
        return sum(1 for c in self._clusters.values() if c["hits"] >= min_hits)

    def any_confirmed(self, min_hits: int) -> bool:
        """Return True if any cluster is confirmed."""
        return self.confirmed_count(min_hits) > 0

    @property
    def clusters(self) -> dict[int, dict]:
        """Read-only cluster state."""
        return self._clusters