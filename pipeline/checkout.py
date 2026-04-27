"""StaticSceneCheckout pipeline implementation."""

from __future__ import annotations

from collections import defaultdict

import cv2
import numpy as np
from ultralytics import YOLO

from .config import PipelineConfig
from .nms import cross_class_nms


class StaticSceneCheckout:
    """Stateful frame-by-frame checkout pipeline for one video session."""

    def __init__(self, cfg: PipelineConfig, price_dict: dict[str, float]) -> None:
        self.cfg = cfg
        self.prices = price_dict
        self.model = YOLO(cfg.model_path)

        self._confirmed_cache: dict[str, int] = {}
        self._class_conf_history: dict[int, list[float]] = defaultdict(list)
        self._class_max_simultaneous: dict[int, int] = defaultdict(int)

        self.frame_count = 0
        self.frames_processed = 0
        self.raw_count = 0
        self.post_nms_count = 0
        self.suppressed_by_nms = 0

    def _conf_threshold(self, label: str) -> float:
        return self.cfg.class_conf_overrides.get(label, self.cfg.conf_threshold)

    def _min_frames(self, label: str) -> int:
        return self.cfg.min_frames_overrides.get(label, self.cfg.min_confirm_frames)

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Run full pipeline on one frame and return annotated frame."""
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

        self._confirmed_cache = self._get_confirmed()
        return self._draw_frame(frame, raw, clean, self._confirmed_cache)

    def _get_confirmed(self) -> dict[str, int]:
        confirmed: dict[str, int] = {}
        for cls, conf_list in self._class_conf_history.items():
            label = self.model.names[cls]
            min_f = self._min_frames(label)
            if len(conf_list) < min_f:
                continue

            if label in self.cfg.qty_overrides:
                qty = self.cfg.qty_overrides[label]
            elif self.cfg.multi_instance:
                qty = self._class_max_simultaneous[cls] or 1
            else:
                qty = 1

            confirmed[label] = qty
        return confirmed

    def get_receipt(self) -> dict:
        """Return confirmed items, computed totals, and processing stats."""
        confirmed = self._get_confirmed()
        items = []
        total = 0.0
        for label, qty in sorted(confirmed.items()):
            unit = self.prices.get(label, 0.0)
            sub = round(unit * qty, 3)
            total += sub
            items.append({"label": label, "qty": qty, "unit_price": unit, "subtotal": sub})

        return {
            "confirmed": confirmed,
            "items": items,
            "total": round(total, 3),
            "stats": {
                "frame_count": self.frame_count,
                "frames_processed": self.frames_processed,
                "raw_detections": self.raw_count,
                "suppressed_by_nms": self.suppressed_by_nms,
                "post_nms_detections": self.post_nms_count,
                "confirmed_products": len(confirmed),
                "model_version": self.cfg.model_path,
            },
        }

    def _draw_frame(self, frame, raw_dets, clean_dets, confirmed):
        """Annotate frame with boxes and summary HUD."""
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