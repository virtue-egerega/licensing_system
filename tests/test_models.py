import pytest
from django.utils import timezone

from core.models import Activation, License, LicenseKey


@pytest.mark.django_db
class TestBrand:
    """Test Brand model."""

    def test_brand_creation(self, brand_rankmath):
        """Test that brand is created correctly."""
        assert brand_rankmath.name == "RankMath"
        assert brand_rankmath.slug == "rankmath"
        assert brand_rankmath.api_key_hash is not None


@pytest.mark.django_db
class TestProduct:
    """Test Product model."""

    def test_product_creation(self, product_rankmath_pro, brand_rankmath):
        """Test that product is created correctly."""
        assert product_rankmath_pro.name == "RankMath Pro"
        assert product_rankmath_pro.slug == "rankmath-pro"
        assert product_rankmath_pro.brand == brand_rankmath
        assert product_rankmath_pro.default_seat_limit == 5


@pytest.mark.django_db
class TestLicenseKey:
    """Test LicenseKey model."""

    def test_license_key_creation(self, license_key_rankmath, brand_rankmath):
        """Test that license key is created correctly."""
        assert license_key_rankmath.brand == brand_rankmath
        assert license_key_rankmath.customer_email == "test@example.com"
        assert "RANKMATH" in license_key_rankmath.key


@pytest.mark.django_db
class TestLicense:
    """Test License model."""

    def test_license_creation(self, license_rankmath_pro, product_rankmath_pro):
        """Test that license is created correctly."""
        assert license_rankmath_pro.product == product_rankmath_pro
        assert license_rankmath_pro.status == License.Status.VALID
        assert license_rankmath_pro.seat_limit == 5

    def test_license_is_valid(self, license_rankmath_pro):
        """Test that license validity check works."""
        assert license_rankmath_pro.is_valid() is True

    def test_license_is_expired(self, license_key_rankmath, product_rankmath_pro):
        """Test that expired license is detected."""
        expired_license = License.objects.create(
            license_key=license_key_rankmath,
            product=product_rankmath_pro,
            status=License.Status.VALID,
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )
        assert expired_license.is_expired() is True
        assert expired_license.is_valid() is False

    def test_license_seat_limit(self, license_rankmath_pro):
        """Test seat limit logic."""
        assert license_rankmath_pro.get_seat_limit() == 5
        assert license_rankmath_pro.has_available_seats() is True

        # Create activations up to the limit
        for i in range(5):
            Activation.objects.create(
                license=license_rankmath_pro,
                instance_identifier=f"https://site{i}.com",
            )

        assert license_rankmath_pro.get_active_activations_count() == 5
        assert license_rankmath_pro.has_available_seats() is False


@pytest.mark.django_db
class TestActivation:
    """Test Activation model."""

    def test_activation_creation(self, activation, license_rankmath_pro):
        """Test that activation is created correctly."""
        assert activation.license == license_rankmath_pro
        assert activation.instance_identifier == "https://example.com"
        assert activation.deactivated_at is None

    def test_activation_deactivation(self, activation):
        """Test that activation can be deactivated."""
        assert activation.deactivated_at is None
        activation.deactivated_at = timezone.now()
        activation.save()
        assert activation.deactivated_at is not None
