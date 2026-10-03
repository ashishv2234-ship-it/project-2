import json
from datetime import UTC, datetime
from typing import Any

from app.models.user import AuditLog
from sqlalchemy.orm import Session


def record_audit_log(
    db: Session,
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str,
    old_value: Any | None = None,
    new_value: Any | None = None,
    ip_address: str | None = None,
):
    """Record an audit trail event."""
    try:
        old_val_str = (
            json.dumps(old_value)
            if isinstance(old_value, (dict, list))
            else (str(old_value) if old_value is not None else None)
        )
        new_val_str = (
            json.dumps(new_value)
            if isinstance(new_value, (dict, list))
            else (str(new_value) if new_value is not None else None)
        )

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            old_value=old_val_str,
            new_value=new_val_str,
            ip_address=ip_address or "127.0.0.1",
            timestamp=datetime.now(UTC),
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:  # noqa: BLE001
        # Never fail the main business transaction because of audit log writing
        db.rollback()
        print(f"[AUDIT LOGGING ERROR]: {e}")
