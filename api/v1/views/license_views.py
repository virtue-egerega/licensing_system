import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers import LicenseStatusResponseSerializer
from core.exceptions import LicenseNotFoundError
from core.services import ActivationService

logger = logging.getLogger(__name__)


class LicenseStatusView(APIView):
    """
    GET /api/v1/licenses/{license_key}/status
    Check license status and entitlements (US4).
    Public endpoint - no authentication required.
    """

    permission_classes = []  # Public endpoint

    def get(self, request, license_key):
        try:
            status_data = ActivationService.get_license_status(license_key)

            serializer = LicenseStatusResponseSerializer(data=status_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except LicenseNotFoundError as e:
            return Response(
                {"error": {"code": "LICENSE_NOT_FOUND", "message": str(e)}},
                status=status.HTTP_404_NOT_FOUND,
            )
