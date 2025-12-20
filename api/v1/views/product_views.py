import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers import ActivationResponseSerializer, CreateActivationSerializer
from core.exceptions import (
    ActivationNotFoundError,
    LicenseCancelledError,
    LicenseExpiredError,
    LicenseNotFoundError,
    LicenseSuspendedError,
    SeatLimitReachedError,
)
from core.services import ActivationService, AuditService

logger = logging.getLogger(__name__)


class CreateActivationView(APIView):
    """
    POST /api/v1/products/activations
    Activate a license for an instance (US3).
    """

    permission_classes = []  # Public endpoint, uses license key for auth

    def post(self, request):
        serializer = CreateActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        license_key = serializer.validated_data["license_key"]
        instance_identifier = serializer.validated_data["instance_identifier"]
        metadata = serializer.validated_data.get("metadata", {})

        try:
            activation = ActivationService.activate_license(
                license_key_str=license_key,
                instance_identifier=instance_identifier,
                metadata=metadata,
            )

            # Audit log
            AuditService.log_action(
                action="activation.created",
                actor=f"license_key:{license_key}",
                entity_type="activation",
                entity_id=activation.id,
                brand=activation.license.product.brand,
                metadata={
                    "license_id": str(activation.license.id),
                    "instance_identifier": instance_identifier,
                },
            )

            response_serializer = ActivationResponseSerializer(activation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except LicenseNotFoundError as e:
            return Response(
                {"error": {"code": "LICENSE_NOT_FOUND", "message": str(e)}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LicenseExpiredError as e:
            return Response(
                {"error": {"code": "LICENSE_EXPIRED", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LicenseSuspendedError as e:
            return Response(
                {"error": {"code": "LICENSE_SUSPENDED", "message": str(e)}},
                status=status.HTTP_403_FORBIDDEN,
            )
        except LicenseCancelledError as e:
            return Response(
                {"error": {"code": "LICENSE_CANCELLED", "message": str(e)}},
                status=status.HTTP_403_FORBIDDEN,
            )
        except SeatLimitReachedError as e:
            return Response(
                {"error": {"code": "SEAT_LIMIT_REACHED", "message": str(e)}},
                status=status.HTTP_409_CONFLICT,
            )


class DeactivateActivationView(APIView):
    """
    DELETE /api/v1/products/activations/{activation_id}
    Deactivate a specific activation (US5).
    """

    permission_classes = []  # Public endpoint

    def delete(self, request, activation_id):
        try:
            activation = ActivationService.deactivate_activation(activation_id)

            # Audit log
            AuditService.log_action(
                action="activation.deactivated",
                actor=f"license_key:{activation.license.license_key.key}",
                entity_type="activation",
                entity_id=activation.id,
                brand=activation.license.product.brand,
                metadata={
                    "license_id": str(activation.license.id),
                    "instance_identifier": activation.instance_identifier,
                },
            )

            response_serializer = ActivationResponseSerializer(activation)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ActivationNotFoundError as e:
            return Response(
                {"error": {"code": "ACTIVATION_NOT_FOUND", "message": str(e)}},
                status=status.HTTP_404_NOT_FOUND,
            )
