"""StaticSceneCheckout pipeline implementation."""

from __future__ import annotations

from collections import defaultdict
import logging

import cv2
import numpy as np
from ultralytics import YOLO

from .config import PipelineConfig
from .nms import cross_class_nms


class StaticSceneCheckout:
    """
    Stateful frame-by-frame checkout pipeline for static-scene retail videos.

    ## How it works

    **Frame-hit accumulation:** This system accumulates per-class confidence detections across
    the entire video in `_class_conf_history`. A product is confirmed when its accumulated
    frame-hit count reaches `min_confirm_frames` (per-class override supported). Products that
    leave the frame before the video ends are still counted correctly at receipt time because
    the history is never reset.

    **Per-class configuration:** A single global threshold assumes the model learned all classes
    equally — it never does. This is why `class_conf_overrides` and `min_frames_overrides` exist.

    **Pipeline per frame:**
      1. YOLO at low global floor (detection_floor)
      2. Per-class confidence filter (class_conf_overrides applied)
      3. Area-based filtering (max_box_ratio)
      4. Cross-class NMS (with family-aware suppression)
      5. Accumulate per-class frame-hit counts
      6. Optionally track objects spatially across frames (ClusterTracker)
      7. Confirm when hits >= min_frames
    """

    def __init__(self, cfg: PipelineConfig, price_dict: dict[str, float]) -> None:
        """
        Initialize checkout pipeline.

        Args:
            cfg: PipelineConfig with all hyperparameters (confidence thresholds, NMS settings, etc)
            price_dict: Map of product label to price in TND
        """
        self.cfg = cfg
        self.prices = price_dict
        self.model = YOLO(cfg.model_path)
        self.logger = logging.getLogger(__name__)
        self.verbose = False  # Set via verbose property if needed

        self._confirmed_cache: dict[str, int] = {}
        self._class_conf_history: dict[int, list[float]] = defaultdict(list)
        self._class_max_simultaneous: dict[int, int] = defaultdict(int)
        self._class_trackers: dict[int, any] = {}  # ClusterTracker per class (optional)

        self.frame_count = 0
        self.frames_processed = 0
        self.raw_count = 0
        self.post_nms_count = 0
        self.suppressed_by_nms = 0

        # Initialize per-class trackers if spatial tracking enabled
        if cfg.use_spatial_tracking:
            from .cluster import ClusterTracker
            for cls in self.model.names.keys():
                self._class_trackers[cls] = ClusterTracker(
                    dist_threshold=cfg.cluster_dist_threshold,
                    ema_alpha=cfg.cluster_ema_alpha,
                    max_lost=cfg.cluster_max_lost,
                )

    def _conf_threshold(self, label: str) -> float:
        """Get per-class or global confidence threshold."""
        return self.cfg.class_conf_overrides.get(label, self.cfg.conf_threshold)

    def _min_frames(self, label: str) -> int:
        """Get per-class or global minimum frame threshold."""
        return self.cfg.min_frames_overrides.get(label, self.cfg.min_confirm_frames)

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Run full pipeline on one frame and return annotated frame.

        Args:
            frame: Input frame as numpy array (H, W, 3) BGR format

        Returns:
            Annotated frame with bounding boxes and HUD overlay
        """
        self.frame_count += 1
        if self.frame_count % self.cfg.frame_skip != 0:
            return self._draw_frame(frame, [], [], self._confirmed_cache)

        self.frames_processed += 1
        h, w = frame.shape[:2]
        max_area = h * w * self.cfg.max_box_ratio

        results = self.model(frame, conf=self.cfg.detection_floor, verbose=False)[0]
        raw: list[list] = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = self.model.names[cls]
            if conf >= self._conf_threshold(label) and (x2 - x1) * (y2 - y1) <= max_area:
                raw.append([x1, y1, x2, y2, conf, cls])

        self.raw_count += len(raw)
        clean = cross_class_nms(
            raw,
            default_iou_threshold=self.cfg.nms_iou_threshold,
            family_iou_threshold=self.cfg.nms_family_iou_threshold,
            model_names=self.model.names,
        )
        self.post_nms_count += len(clean)
        self.suppressed_by_nms += len(raw) - len(clean)

        frame_cls_conf: dict[int, float] = defaultdict(float)
        frame_cls_count: dict[int, int] = defaultdict(int)
        for det in clean:
            cls = int(det[5])
            conf = float(det[4])
            frame_cls_count[cls] += 1
            if conf > frame_cls_conf[cls]:
                frame_cls_conf[cls] = conf

        for cls, best_conf in frame_cls_conf.items():
            self._class_conf_history[cls].append(best_conf)
        for cls, count in frame_cls_count.items():
            if count > self._class_max_simultaneous[cls]:
                self._class_max_simultaneous[cls] = count

        # Optionally update spatial trackers
        if self.cfg.use_spatial_tracking:
            for det in clean:
                cls = int(det[5])
                if cls in self._class_trackers:
                    self._class_trackers[cls].update([det[:4]])

        self._confirmed_cache = self._get_confirmed()
        return self._draw_frame(frame, raw, clean, self._confirmed_cache)

    def _get_confirmed(self) -> dict[str, int]:
        """
        Get confirmed products based on frame-hit accumulation.

        Returns:
            Dict mapping label to quantity
        """
        confirmed: dict[str, int] = {}
        for cls, conf_list in self._class_conf_history.items():
            label = self.model.names[cls]
            min_f = self._min_frames(label)
            if len(conf_list) < min_f:
                continue

            if label in self.cfg.qty_overrides:
                qty = self.cfg.qty_overrides[label]
            elif self.cfg.multi_instance:
                qty = max(1, self._class_max_simultaneous[cls])
            else:
                qty = 1

            confirmed[label] = qty
        return confirmed

    def get_receipt(self) -> dict:
        """
        Get final receipt with items, totals, diagnostics, and processing stats.

        Includes per-class frame-hit diagnostics to help tune min_frames_overrides and
        class_conf_overrides. Diagnostics show which classes fell short of confirmation.

        Returns:
            Dict with keys: confirmed, items, total, diagnostics, stats
        """
        confirmed = self._get_confirmed()
        items = []
        total = 0.0

        diagnostics = []
        diagnostics_by_label: dict[str, dict] = {}
        for cls, conf_list in sorted(self._class_conf_history.items(), key=lambda x: -len(x[1])):
            label = self.model.names[cls]
            min_f = self._min_frames(label)
            min_c = self._conf_threshold(label)
            avg_c = float(np.mean(conf_list)) if conf_list else 0.0
            status = "OK" if len(conf_list) >= min_f else "X (needs tuning)"
            summary = {
                "label": label,
                "frame_hits": len(conf_list),
                "avg_confidence": round(avg_c, 3),
                "min_required_frames": min_f,
                "min_required_confidence": min_c,
                "status": status,
            }
            diagnostics.append(summary)
            diagnostics_by_label[label] = summary

        for label, qty in sorted(confirmed.items()):
            unit = self.prices.get(label, 0.0)
            sub = round(unit * qty, 3)
            total += sub
            items.append({
                "label": label,
                "qty": qty,
                "unit_price": unit,
                "subtotal": sub,
                "confidence": diagnostics_by_label.get(label, {}).get("avg_confidence"),
            })

        # Print verbose diagnostics if enabled
        if self.verbose:
            self._print_receipt_diagnostics(items, total, diagnostics)

        return {
            "confirmed": confirmed,
            "items": items,
            "total": round(total, 3),
            "diagnostics": diagnostics,
            "stats": {
                "frame_count": self.frame_count,
                "frames_processed": self.frames_processed,
                "raw_detections": self.raw_count,
                "suppressed_by_nms": self.suppressed_by_nms,
                "nms_suppression_rate": round(100 * self.suppressed_by_nms / max(self.raw_count, 1), 1),
                "post_nms_detections": self.post_nms_count,
                "confirmed_products": len(confirmed),
                "model_version": self.cfg.model_path,
            },
        }

    def _print_receipt_diagnostics(self, items: list, total: float, diagnostics: list) -> None:
        """Print formatted receipt and per-class diagnostics (verbose mode)."""
        print("\n" + "=" * 60)
        print("              FINAL RECEIPT  —  ACOS CHECKOUT")
        print("=" * 60)
        for item in items:
            print(f"  {item['label']:40s} x{item['qty']} "
                  f"{item['subtotal']:7.2f} TND")
        print("-" * 60)
        print(f"  {'TOTAL':40s}     {total:7.2f} TND")
        print("=" * 60)

        print("\n  Per-class frame-hit diagnostics (sorted by frame count):")
        for diag in diagnostics:
            status_mark = "✓" if diag["status"] == "OK" else "✗"
            print(f"  [{status_mark}] {diag['label']:40s} frames={diag['frame_hits']:4d}  "
                  f"avg_conf={diag['avg_confidence']:5.2f}  "
                  f"(min_conf={diag['min_required_confidence']:.2f}, "
                  f"min_frames={diag['min_required_frames']})")

        print(f"\n  Pipeline stats:")
        print(f"    Total frames      : {self.frame_count}")
        print(f"    Processed frames  : {self.frames_processed}")
        print(f"    Raw detections    : {self.raw_count}")
        print(f"    NMS suppression   : {self.suppressed_by_nms} "
              f"({round(100*self.suppressed_by_nms/max(self.raw_count,1), 1)}%)")
        print(f"    After NMS         : {self.post_nms_count}")
        print(f"    Confirmed         : {len([d for d in diagnostics if d['status'] == 'OK'])}")
        print("=" * 60 + "\n")

    def _draw_frame(self, frame, raw_dets, clean_dets, confirmed):
        """Annotate frame with detection boxes and checkout summary HUD."""
        h, w = frame.shape[:2]
        clean_set = {(round(d[0]), round(d[1]), round(d[2]), round(d[3])) for d in clean_dets}

        for d in raw_dets:
            key = (round(d[0]), round(d[1]), round(d[2]), round(d[3]))
            if key not in clean_set:
                cv2.rectangle(
                    frame,
                    (int(d[0]), int(d[1])),
                    (int(d[2]), int(d[3])),
                    (40, 40, 160),
                    1,
                )

        for d in clean_dets:
            x1, y1, x2, y2 = map(int, d[:4])
            label = self.model.names[int(d[5])]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 215, 0), 2)
            cv2.putText(
                frame,
                f"{label} {d[4]:.2f}",
                (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (0, 215, 0),
                2,
            )

        y = 30
        cv2.putText(frame, "=== CHECKOUT ===", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 230, 0), 2)
        y += 26
        cv2.putText(
            frame,
            f"frame {self.frame_count} | NMS sup: {self.suppressed_by_nms}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (160, 160, 160),
            1,
        )
        y += 20

        running_total = 0.0
        for label, qty in sorted(confirmed.items()):
            unit = self.prices.get(label, 0)
            sub = unit * qty
            running_total += sub
            cv2.putText(
                frame,
                f"{label}  x{qty}  {sub:.2f} TND",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.46,
                (255, 230, 0),
                1,
            )
            y += 19

        cv2.rectangle(frame, (5, h - 38), (w - 5, h - 5), (0, 220, 220), 2)
        cv2.putText(
            frame,
            f"TOTAL: {running_total:.2f} TND  |  {len(confirmed)} products",
            (10, h - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (0, 220, 220),
            2,
        )
        return frame
