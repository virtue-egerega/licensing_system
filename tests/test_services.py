import pytest
from django.utils import timezone

from core.exceptions import (
    LicenseAlreadyExistsError,
    LicenseExpiredError,
    LicenseNotFoundError,
    SeatLimitReachedError,
)
from core.models import Activation, License
from core.services import ActivationService, LicenseService


@pytest.mark.django_db
class TestLicenseService:
    """Test LicenseService."""

    def test_generate_license_key(self, brand_rankmath):
        """Test license key generation."""
        license_key = LicenseService.generate_license_key(
            brand_rankmath, "newcustomer@example.com"
        )

        assert license_key.brand == brand_rankmath
        assert license_key.customer_email == "newcustomer@example.com"
        assert "RANKMATH" in license_key.key

    def test_create_license(self, brand_rankmath, product_rankmath_pro):
        """Test license creation."""
        license_obj = LicenseService.create_license(
            brand=brand_rankmath,
            customer_email="customer@example.com",
            product_slug="rankmath-pro",
            expires_at=timezone.now() + timezone.timedelta(days=365),
            seat_limit=10,
        )

        assert license_obj.product == product_rankmath_pro
        assert license_obj.status == License.Status.VALID
        assert license_obj.seat_limit == 10

    def test_create_license_duplicate(
        self, brand_rankmath, product_rankmath_pro, license_key_rankmath
    ):
        """Test that duplicate license creation raises error."""
        LicenseService.create_license(
            brand=brand_rankmath,
            customer_email="test@example.com",
            product_slug="rankmath-pro",
            license_key_str=license_key_rankmath.key,
        )

        with pytest.raises(LicenseAlreadyExistsError):
            LicenseService.create_license(
                brand=brand_rankmath,
                customer_email="test@example.com",
                product_slug="rankmath-pro",
                license_key_str=license_key_rankmath.key,
            )

    def test_update_license_status(self, license_rankmath_pro):
        """Test updating license status."""
        updated_license = LicenseService.update_license_status(
            license_id=license_rankmath_pro.id,
            status=License.Status.SUSPENDED,
            expires_at=None,
        )

        assert updated_license.status == License.Status.SUSPENDED

    def test_get_licenses_by_email(
        self,
        brand_rankmath,
        brand_wprocket,
        product_rankmath_pro,
        product_wprocket_standard,
    ):
        """Test getting all licenses for an email across brands."""
        email = "multi@example.com"

        # Create licenses for both brands
        LicenseService.create_license(
            brand=brand_rankmath,
            customer_email=email,
            product_slug="rankmath-pro",
        )

        LicenseService.create_license(
            brand=brand_wprocket,
            customer_email=email,
            product_slug="wprocket-standard",
        )

        licenses = LicenseService.get_licenses_by_email(email)
        assert len(licenses) == 2


@pytest.mark.django_db
class TestActivationService:
    """Test ActivationService."""

    def test_activate_license(self, license_rankmath_pro):
        """Test license activation."""
        activation = ActivationService.activate_license(
            license_key_str=license_rankmath_pro.license_key.key,
            instance_identifier="https://newsite.com",
            metadata={"version": "2.0.0"},
        )

        assert activation.license == license_rankmath_pro
        assert activation.instance_identifier == "https://newsite.com"
        assert activation.metadata["version"] == "2.0.0"

    def test_activate_license_idempotent(self, license_rankmath_pro):
        """Test that activating same instance twice returns same activation."""
        activation1 = ActivationService.activate_license(
            license_key_str=license_rankmath_pro.license_key.key,
            instance_identifier="https://same-site.com",
        )

        activation2 = ActivationService.activate_license(
            license_key_str=license_rankmath_pro.license_key.key,
            instance_identifier="https://same-site.com",
        )

        assert activation1.id == activation2.id

    def test_activate_license_seat_limit(self, license_rankmath_pro):
        """Test that seat limit is enforced."""
        # Activate up to the limit
        for i in range(5):
            ActivationService.activate_license(
                license_key_str=license_rankmath_pro.license_key.key,
                instance_identifier=f"https://site{i}.com",
            )

        # Try to activate one more
        with pytest.raises(SeatLimitReachedError):
            ActivationService.activate_license(
                license_key_str=license_rankmath_pro.license_key.key,
                instance_identifier="https://onemore.com",
            )

    def test_activate_expired_license(self, license_key_rankmath, product_rankmath_pro):
        """Test that expired license cannot be activated."""
        expired_license = License.objects.create(
            license_key=license_key_rankmath,
            product=product_rankmath_pro,
            status=License.Status.VALID,
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )

        with pytest.raises(LicenseExpiredError):
            ActivationService.activate_license(
                license_key_str=license_key_rankmath.key,
                instance_identifier="https://test.com",
            )

    def test_deactivate_activation(self, activation):
        """Test deactivating an activation."""
        deactivated = ActivationService.deactivate_activation(activation.id)

        assert deactivated.deactivated_at is not None

    def test_get_license_status(self, license_rankmath_pro):
        """Test getting license status."""
        status_data = ActivationService.get_license_status(
            license_rankmath_pro.license_key.key
        )

        assert status_data["license_key"] == license_rankmath_pro.license_key.key
        assert status_data["customer_email"] == "test@example.com"
        assert status_data["valid"] is True
        assert len(status_data["licenses"]) == 1

    def test_get_license_status_not_found(self):
        """Test that invalid license key raises error."""
        with pytest.raises(LicenseNotFoundError):
            ActivationService.get_license_status("INVALID-KEY")
