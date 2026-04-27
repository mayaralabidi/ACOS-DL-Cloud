"""Run the ML pipeline on uploaded video files."""

import logging
import os

from sqlalchemy import select

from ..config import get_settings
from ..db import AsyncSessionLocal
from ..models.receipt_item import ReceiptItem
from ..models.session import Session, SessionStatus
from ..services.model_metadata import load_model_metadata
from ..services.storage import download_model_if_needed
from pipeline.checkout import StaticSceneCheckout
from pipeline.config import PipelineConfig
from pipeline.prices import PRICES

logger = logging.getLogger(__name__)
settings = get_settings()


async def run_inference(session_id: str, video_path: str) -> None:
    """Background task that processes a video and persists receipt output."""
    import cv2

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            logger.error("Session %s not found", session_id)
            return

        try:
            model_path = download_model_if_needed()
            model_meta = load_model_metadata(model_path=model_path)
            cfg = PipelineConfig(
                model_path=model_path,
                multi_instance=settings.multi_instance,
                conf_threshold=settings.conf_threshold,
                detection_floor=settings.detection_floor,
                min_confirm_frames=settings.min_confirm_frames,
                nms_iou_threshold=settings.nms_iou_threshold,
                nms_family_iou_threshold=settings.nms_family_iou_threshold,
                cluster_dist_threshold=settings.cluster_dist_threshold,
                cluster_ema_alpha=settings.cluster_ema_alpha,
                cluster_max_lost=settings.cluster_max_lost,
                frame_skip=settings.frame_skip,
            )
            checkout = StaticSceneCheckout(cfg, PRICES)

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video: {video_path}")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                checkout.process_frame(frame)
            cap.release()

            receipt = checkout.get_receipt()
            session.receipt_raw = receipt
            session.total = receipt["total"]
            session.frame_count = receipt["stats"]["frame_count"]
            session.model_version = model_meta["model_version"]
            session.status = SessionStatus.ready

            for item in receipt["items"]:
                db.add(
                    ReceiptItem(
                        session_id=session.id,
                        label=item["label"],
                        qty=item["qty"],
                        unit_price=item["unit_price"],
                        subtotal=item["subtotal"],
                        is_override=False,
                    )
                )
        except Exception as exc:
            logger.exception("Inference failed for session %s", session_id)
            session.status = SessionStatus.cancelled
            session.error = str(exc)
        finally:
            try:
                os.unlink(video_path)
            except OSError:
                pass
            await db.commit()