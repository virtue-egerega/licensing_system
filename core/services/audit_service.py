import logging
import uuid

from core.models import AuditLog, Brand

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for audit logging of all license operations.
    """

    @staticmethod
    def log_action(
        action: str,
        actor: str,
        entity_type: str,
        entity_id: uuid.UUID,
        brand: Brand = None,
        metadata: dict = None,
    ) -> AuditLog:
        """
        Log an action in the audit trail.

        Args:
            action: Action name (e.g., "license.created", "activation.deactivated")
            actor: Identifier of who performed the action (e.g., API key, user ID)
            entity_type: Type of entity (e.g., "license", "activation")
            entity_id: ID of the affected entity
            brand: Optional brand associated with the action
            metadata: Additional contextual data
        """
        audit_log = AuditLog.objects.create(
            brand=brand,
            action=action,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )

        logger.info(
            f"Audit: {action} by {actor} on {entity_type}:{entity_id} "
            f"(Brand: {brand.name if brand else 'N/A'})"
        )

        return audit_log
