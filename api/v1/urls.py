from django.urls import path

from .views import (
    CreateActivationView,
    CreateLicenseKeyView,
    CreateLicenseView,
    DeactivateActivationView,
    LicenseStatusView,
    ListLicensesByEmailView,
    UpdateLicenseView,
)

urlpatterns = [
    # Brand APIs (US1, US2, US6)
    path(
        "brands/license-keys",
        CreateLicenseKeyView.as_view(),
        name="create-license-key",
    ),
    path(
        "brands/licenses/<uuid:license_id>",
        UpdateLicenseView.as_view(),
        name="update-license",
    ),
    path(
        "brands/licenses/search",
        ListLicensesByEmailView.as_view(),
        name="list-licenses-by-email",
    ),
    path("brands/licenses", CreateLicenseView.as_view(), name="create-license"),
    # Product APIs (US3, US5)
    path(
        "products/activations",
        CreateActivationView.as_view(),
        name="create-activation",
    ),
    path(
        "products/activations/<uuid:activation_id>",
        DeactivateActivationView.as_view(),
        name="deactivate-activation",
    ),
    # Public APIs (US4)
    path(
        "licenses/<str:license_key>/status",
        LicenseStatusView.as_view(),
        name="license-status",
    ),
]
