"""Session endpoints for processing and receipt lifecycle."""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dependencies import get_db
from ..models.session import Session, SessionStatus
from ..schemas.session import OverrideRequest, SessionResponse
from ..services.inference import run_inference
from ..services.receipt import apply_override

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MiB


async def _load_session_with_items(db: AsyncSession, session_id: str) -> Session | None:
    """Load a session and eagerly include receipt_items for response serialization."""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.receipt_items))
        .where(Session.id == session_id)
    )
    return result.scalar_one_or_none()


@router.post("/process", response_model=SessionResponse, status_code=202)
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a video and start async inference in the background."""
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=422, detail="File must be a video")

    session = Session()
    db.add(session)
    await db.commit()
    await db.refresh(session)

    suffix = Path(file.filename).suffix if file.filename else ".mp4"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await file.read(UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = tmp.name
    finally:
        await file.close()

    background_tasks.add_task(run_inference, session.id, tmp_path)
    loaded = await _load_session_with_items(db, session.id)
    return loaded or session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch a session by id."""
    session = await _load_session_with_items(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List sessions ordered by creation date."""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.receipt_items))
        .order_by(Session.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.patch("/{session_id}/override", response_model=SessionResponse)
async def override_receipt(
    session_id: str,
    body: OverrideRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add/remove an item manually while session is in ready state."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status not in (SessionStatus.ready,):
        raise HTTPException(status_code=409, detail="Session is not in ready state")

    await apply_override(db, session, body)
    await db.commit()
    refreshed = await _load_session_with_items(db, session_id)
    return refreshed or session


@router.post("/{session_id}/confirm", response_model=SessionResponse)
async def confirm_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Confirm final receipt and lock the session."""
    from datetime import datetime, timezone

    from ..models.receipt_item import ReceiptItem

    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatus.ready:
        raise HTTPException(status_code=409, detail="Session is not ready to confirm")

    session.status = SessionStatus.confirmed
    session.confirmed_at = datetime.now(timezone.utc)

    items_result = await db.execute(select(ReceiptItem).where(ReceiptItem.session_id == session_id))
    items = items_result.scalars().all()
    session.receipt_final = {
        "items": [
            {
                "label": i.label,
                "qty": i.qty,
                "unit_price": i.unit_price,
                "subtotal": i.subtotal,
                "is_override": i.is_override,
            }
            for i in items
        ],
        "total": session.total,
    }
    await db.commit()
    refreshed = await _load_session_with_items(db, session_id)
    return refreshed or session


@router.delete("/{session_id}", status_code=204)
async def cancel_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = SessionStatus.cancelled
    await db.commit()