from datetime import UTC, datetime
from typing import Any

from app.core.database import get_db
from app.schemas.offline_sync import (
    DeltaSyncRequest,
    DeltaSyncResponse,
    SyncBatchRequest,
    SyncBatchResponse,
)
from app.services.offline_sync_engine import offline_sync_engine
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/sync",
    tags=["Offline Synchronization"],
)


@router.post(
    "/batch",
    response_model=SyncBatchResponse,
)
def synchronize_batch(
    payload: SyncBatchRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Process an offline synchronization batch from a field device.
    """
    try:
        result = offline_sync_engine.process_sync_batch(
            db=db,
            user_id=payload.device_id,
            device_id=payload.device_id,
            queue_items=[item.model_dump(mode="json") for item in payload.queue_items],
        )

        return {
            "sync_session_id": payload.sync_session_id,
            **result,
        }

    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid synchronization data: {exc}",
        ) from exc


@router.get("/status")
def get_sync_status(
    last_synced_at: str | None = None,
) -> dict[str, Any]:
    """
    Return synchronization status for an offline client.
    """
    cursor_dt = None

    if last_synced_at:
        try:
            cursor_dt = datetime.fromisoformat(last_synced_at)
        except (TypeError, ValueError):
            cursor_dt = None

    return {
        "status": "ready",
        "last_synced_at": last_synced_at,
        "cursor": (cursor_dt.isoformat() if cursor_dt is not None else None),
        "server_time": datetime.now(UTC).isoformat(),
    }


@router.post(
    "/push",
    response_model=SyncBatchResponse,
)
def push_offline_data(
    payload: SyncBatchRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Push queued offline records to the central backend.
    """
    try:
        result = offline_sync_engine.process_sync_batch(
            db=db,
            user_id=payload.device_id,
            device_id=payload.device_id,
            queue_items=[item.model_dump(mode="json") for item in payload.queue_items],
        )

        return {
            "sync_session_id": payload.sync_session_id,
            **result,
        }

    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to synchronize offline data: {exc}",
        ) from exc


@router.post(
    "/pull",
    response_model=DeltaSyncResponse,
)
def pull_latest_data(
    payload: DeltaSyncRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Retrieve updates for an offline client.

    The current offline synchronization engine does not expose
    a delta-sync retrieval method, so this endpoint reports that
    the pull operation is not yet implemented.
    """
    del db

    raise HTTPException(
        status_code=501,
        detail=(
            "Delta synchronization is not implemented by the "
            "current offline synchronization engine."
        ),
    )
