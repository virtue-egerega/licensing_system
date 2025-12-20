from rest_framework.views import exception_handler

from .brand_views import (
    CreateLicenseKeyView,
    CreateLicenseView,
    ListLicensesByEmailView,
    UpdateLicenseView,
)
from .license_views import LicenseStatusView
from .product_views import CreateActivationView, DeactivateActivationView


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        custom_response = {"error": {"message": str(exc), "details": response.data}}
        response.data = custom_response

    return response


__all__ = [
    "CreateLicenseKeyView",
    "CreateLicenseView",
    "ListLicensesByEmailView",
    "UpdateLicenseView",
    "LicenseStatusView",
    "CreateActivationView",
    "DeactivateActivationView",
    "custom_exception_handler",
]
