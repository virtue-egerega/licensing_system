import logging
import uuid

from django.db import transaction
from django.utils import timezone

from core.exceptions import (
    ActivationNotFoundError,
    LicenseCancelledError,
    LicenseExpiredError,
    LicenseNotFoundError,
    LicenseSuspendedError,
    SeatLimitReachedError,
)
from core.models import Activation, License, LicenseKey

logger = logging.getLogger(__name__)


class ActivationService:
    """
    Service for managing license activations and seat enforcement (US3, US5).
    """

    @staticmethod
    @transaction.atomic
    def activate_license(
        license_key_str: str, instance_identifier: str, metadata: dict = None
    ) -> Activation:
        """
        Activate a license for a specific instance (US3).
        Enforces seat limits and validates license status.
        """
        # Get license key
        try:
            license_key = LicenseKey.objects.get(key=license_key_str)
        except LicenseKey.DoesNotExist:
            raise LicenseNotFoundError(f"License key {license_key_str} not found")

        # For now, we'll activate the first valid license
        # In practice, you might want to specify which product to activate
        valid_licenses = license_key.licenses.filter(status=License.Status.VALID)

        if not valid_licenses.exists():
            raise LicenseNotFoundError(
                f"No valid licenses found for key {license_key_str}"
            )

        # Try to activate each license (for multi-product scenarios)
        activation = None
        last_error = None
        for license_obj in valid_licenses:
            try:
                activation = ActivationService._activate_single_license(
                    license_obj, instance_identifier, metadata
                )
                break  # Successfully activated
            except (
                LicenseExpiredError,
                LicenseSuspendedError,
                LicenseCancelledError,
                SeatLimitReachedError,
            ) as e:
                # Try next license
                logger.warning(f"Could not activate license {license_obj.id}: {e}")
                last_error = e
                continue

        if activation is None:
            # If we have a specific error from the last attempt, raise it
            if last_error:
                raise last_error
            # Otherwise, no licenses were found
            raise LicenseNotFoundError(
                f"No activatable licenses found for key {license_key_str}"
            )

        return activation

    @staticmethod
    def _activate_single_license(
        license_obj: License, instance_identifier: str, metadata: dict = None
    ) -> Activation:
        """
        Activate a single license with validation.
        """
        # Validate license status
        if license_obj.status == License.Status.SUSPENDED:
            raise LicenseSuspendedError(
                f"License {license_obj.id} is suspended and cannot be activated"
            )

        if license_obj.status == License.Status.CANCELLED:
            raise LicenseCancelledError(
                f"License {license_obj.id} is cancelled and cannot be activated"
            )

        # Check expiration
        if license_obj.is_expired():
            raise LicenseExpiredError(
                f"License {license_obj.id} expired at {license_obj.expires_at}"
            )

        # Check for existing activation (idempotent)
        existing_activation = Activation.objects.filter(
            license=license_obj,
            instance_identifier=instance_identifier,
            deactivated_at__isnull=True,
        ).first()

        if existing_activation:
            logger.info(
                f"Activation already exists for instance {instance_identifier}, returning existing"
            )
            return existing_activation

        # Check seat limit
        if not license_obj.has_available_seats():
            seat_limit = license_obj.get_seat_limit()
            seats_used = license_obj.get_active_activations_count()
            raise SeatLimitReachedError(
                f"Seat limit of {seat_limit} reached for license {license_obj.id} "
                f"({seats_used}/{seat_limit} seats used)"
            )

        # Create activation
        activation = Activation.objects.create(
            license=license_obj,
            instance_identifier=instance_identifier,
            metadata=metadata or {},
        )

        logger.info(
            f"Activated license {license_obj.id} for instance {instance_identifier} "
            f"(activation: {activation.id})"
        )

        return activation

    @staticmethod
    def deactivate_activation(activation_id: uuid.UUID) -> Activation:
        """
        Deactivate a specific activation (US5).
        Frees up a seat for reuse.
        """
        try:
            activation = Activation.objects.get(id=activation_id)
        except Activation.DoesNotExist:
            raise ActivationNotFoundError(f"Activation {activation_id} not found")

        if activation.deactivated_at is not None:
            logger.warning(
                f"Activation {activation_id} is already deactivated, ignoring"
            )
            return activation

        activation.deactivated_at = timezone.now()
        activation.save()

        logger.info(
            f"Deactivated activation {activation_id} for license {activation.license.id}"
        )

        return activation

    @staticmethod
    def get_license_status(license_key_str: str) -> dict:
        """
        Get status and entitlements for a license key (US4).
        """
        try:
            license_key = LicenseKey.objects.get(key=license_key_str)
        except LicenseKey.DoesNotExist:
            raise LicenseNotFoundError(f"License key {license_key_str} not found")

        licenses = license_key.licenses.select_related("product").all()

        license_data = []
        for license_obj in licenses:
            seats_used = license_obj.get_active_activations_count()
            seats_total = license_obj.get_seat_limit()

            license_data.append(
                {
                    "license_id": str(license_obj.id),
                    "product": license_obj.product.name,
                    "product_slug": license_obj.product.slug,
                    "status": license_obj.status,
                    "expires_at": (
                        license_obj.expires_at.isoformat()
                        if license_obj.expires_at
                        else None
                    ),
                    "seats_used": seats_used,
                    "seats_total": seats_total,
                    "is_valid": license_obj.is_valid(),
                }
            )

        result = {
            "license_key": license_key_str,
            "customer_email": license_key.customer_email,
            "valid": any(lic["is_valid"] for lic in license_data),
            "licenses": license_data,
        }

        logger.info(f"Retrieved status for license key {license_key_str}")

        return result
