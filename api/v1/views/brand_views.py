import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.permissions import IsBrandAuthenticated
from api.v1.serializers import (
    CreateLicenseKeySerializer,
    CreateLicenseSerializer,
    LicenseKeyResponseSerializer,
    LicenseResponseSerializer,
    UpdateLicenseSerializer,
)
from core.exceptions import LicenseAlreadyExistsError, ProductNotFoundError
from core.models import License
from core.services import AuditService, LicenseService

logger = logging.getLogger(__name__)


class CreateLicenseKeyView(APIView):
    """
    POST /api/v1/brands/license-keys
    Create a new license key for a customer.
    """

    permission_classes = [IsBrandAuthenticated]

    def post(self, request):
        serializer = CreateLicenseKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        brand = request.auth
        customer_email = serializer.validated_data["customer_email"]

        # Generate license key
        license_key = LicenseService.generate_license_key(brand, customer_email)

        # Audit log
        AuditService.log_action(
            action="license_key.created",
            actor=f"brand:{brand.slug}",
            entity_type="license_key",
            entity_id=license_key.id,
            brand=brand,
            metadata={"customer_email": customer_email},
        )

        response_serializer = LicenseKeyResponseSerializer(license_key)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CreateLicenseView(APIView):
    """
    POST /api/v1/brands/licenses
    Create a license for a product (US1).
    """

    permission_classes = [IsBrandAuthenticated]

    def post(self, request):
        serializer = CreateLicenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        brand = request.auth

        try:
            license_obj = LicenseService.create_license(
                brand=brand,
                customer_email=serializer.validated_data["customer_email"],
                product_slug=serializer.validated_data["product_slug"],
                license_key_str=serializer.validated_data.get("license_key"),
                expires_at=serializer.validated_data.get("expires_at"),
                seat_limit=serializer.validated_data.get("seat_limit"),
            )

            # Audit log
            AuditService.log_action(
                action="license.created",
                actor=f"brand:{brand.slug}",
                entity_type="license",
                entity_id=license_obj.id,
                brand=brand,
                metadata={
                    "product_slug": serializer.validated_data["product_slug"],
                    "customer_email": serializer.validated_data["customer_email"],
                },
            )

            response_serializer = LicenseResponseSerializer(license_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ProductNotFoundError as e:
            return Response(
                {"error": {"code": "PRODUCT_NOT_FOUND", "message": str(e)}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LicenseAlreadyExistsError as e:
            return Response(
                {"error": {"code": "LICENSE_ALREADY_EXISTS", "message": str(e)}},
                status=status.HTTP_409_CONFLICT,
            )
        except ValueError as e:
            return Response(
                {"error": {"code": "INVALID_REQUEST", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListLicensesByEmailView(APIView):
    """
    GET /api/v1/brands/licenses?customer_email=user@example.com
    List all licenses for a customer email across all brands (US6).
    Brand-only access.
    """

    permission_classes = [IsBrandAuthenticated]

    def get(self, request):
        customer_email = request.query_params.get("customer_email")

        if not customer_email:
            return Response(
                {
                    "error": {
                        "code": "MISSING_PARAMETER",
                        "message": "customer_email parameter is required",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        licenses = LicenseService.get_licenses_by_email(customer_email)

        # Audit log
        brand = request.auth
        AuditService.log_action(
            action="licenses.listed_by_email",
            actor=f"brand:{brand.slug}",
            entity_type="license",
            entity_id=brand.id,
            brand=brand,
            metadata={"customer_email": customer_email, "count": len(licenses)},
        )

        serializer = LicenseResponseSerializer(licenses, many=True)
        return Response(
            {"customer_email": customer_email, "licenses": serializer.data},
            status=status.HTTP_200_OK,
        )


class UpdateLicenseView(APIView):
    """
    PATCH /api/v1/brands/licenses/{license_id}
    Update license status or expiration (US2).
    """

    permission_classes = [IsBrandAuthenticated]

    def patch(self, request, license_id):
        serializer = UpdateLicenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        brand = request.auth

        # Verify the license belongs to this brand
        try:
            License.objects.get(id=license_id, license_key__brand=brand)
        except License.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "LICENSE_NOT_FOUND",
                        "message": (
                            f"License {license_id} not found "
                            "or does not belong to this brand"
                        ),
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update license
        updated_license = LicenseService.update_license_status(
            license_id=license_id,
            status=serializer.validated_data.get("status"),
            expires_at=serializer.validated_data.get("expires_at"),
        )

        # Audit log
        AuditService.log_action(
            action="license.updated",
            actor=f"brand:{brand.slug}",
            entity_type="license",
            entity_id=license_id,
            brand=brand,
            metadata={
                "status": serializer.validated_data.get("status"),
                "expires_at": str(serializer.validated_data.get("expires_at")),
            },
        )

        response_serializer = LicenseResponseSerializer(updated_license)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
