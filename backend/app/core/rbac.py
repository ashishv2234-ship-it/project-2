from enum import Enum

from fastapi import HTTPException, status


class UserRole(str, Enum):
    SUPER_ADMIN = "Super Admin"
    STATE_ADMIN = "State Admin"
    DISTRICT_OFFICER = "District Officer"
    FIELD_OFFICER = "Field Officer"
    DISPATCHER = "Dispatcher"
    DRIVER = "Driver"
    VIEWER = "Viewer"


ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: {"*"},
    UserRole.STATE_ADMIN: {
        "user:manage:state",
        "route:plan",
        "route:assign",
        "route:reoptimize",
        "incident:report",
        "incident:verify",
        "incident:resolve",
        "alert:create",
        "alert:notify",
        "vehicle:track",
        "vehicle:manage",
        "emergency:activate",
        "dashboard:read",
        "audit:read",
        "risk:recompute",
    },
    UserRole.DISTRICT_OFFICER: {
        "route:plan",
        "route:assign",
        "incident:report",
        "incident:verify",
        "incident:resolve",
        "alert:create",
        "alert:notify:district",
        "vehicle:track",
        "dashboard:read",
        "network:status:write",
        "emergency:activate:district",
    },
    UserRole.FIELD_OFFICER: {
        "incident:report",
        "field_report:sync",
        "media:upload",
        "vehicle:track:local",
        "network:status:propose",
        "dashboard:read:limited",
    },
    UserRole.DISPATCHER: {
        "route:plan",
        "route:assign",
        "route:reoptimize",
        "vehicle:track",
        "vehicle:manage",
        "consignments:manage",
        "trips:manage",
        "dashboard:read",
        "alert:create",
    },
    UserRole.DRIVER: {
        "vehicle:track:self",
        "gps:ingest:self",
        "trips:read:self",
        "delivery:proof:upload",
        "field_report:create",
        "sos:distress",
    },
    UserRole.VIEWER: {
        "dashboard:read",
        "vehicle:track:public",
        "network:status:read",
        "weather:read",
    },
}


def has_permission(user_role: str, required_permission: str) -> bool:
    try:
        role_enum = UserRole(user_role)
    except ValueError:
        return False

    role_perms: set[str] = ROLE_PERMISSIONS.get(role_enum, set())
    if "*" in role_perms:
        return True

    if required_permission in role_perms:
        return True

    # Check wildcard prefixes e.g. "route:*"
    prefix = required_permission.split(":")[0] + ":*"
    return prefix in role_perms

    return False


def require_permission(user_role: str, permission: str):
    if not has_permission(user_role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Role '{user_role}' lacks permission '{permission}'",
        )
