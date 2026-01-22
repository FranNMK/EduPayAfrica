"""
Platform Admin API and Utilities
Provides programmatic access to platform admin functions.
"""

from django.contrib.auth import get_user_model
from .models import AuditLog, Institution, PlatformUserProfile, SystemStatus

User = get_user_model()


def record_audit_log(
    action: str,
    actor: User | None = None,
    entity_type: str = "",
    entity_id: str = "",
    description: str = "",
) -> AuditLog:
    """
    Programmatically record an action to the audit log.

    Args:
        action: Short description of action performed.
        actor: User who performed the action.
        entity_type: Type of entity affected (institution, user, setting, etc).
        entity_id: ID or identifier of the entity.
        description: Longer description of the action.

    Returns:
        The created AuditLog record.
    """
    return AuditLog.record(
        action=action,
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )


def get_or_create_user_profile(user: User) -> PlatformUserProfile:
    """Get or create a PlatformUserProfile for a user."""
    return PlatformUserProfile.objects.get_or_create(user=user)[0]


def set_system_status(is_operational: bool, message: str = "", actor: User | None = None) -> SystemStatus:
    """Update the system operational status."""
    status, _ = SystemStatus.objects.get_or_create(id=1)
    status.is_operational = is_operational
    status.message = message or ("Operational" if is_operational else "Degraded")
    status.updated_by = actor
    status.save()
    return status
