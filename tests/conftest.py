import hashlib

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Activation, Brand, License, LicenseKey, Product


@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    return APIClient()


@pytest.fixture
def brand_rankmath(db):
    """Create a RankMath brand for testing."""
    api_key = "test-api-key-rankmath"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    brand = Brand.objects.create(
        name="RankMath",
        slug="rankmath",
        api_key_hash=api_key_hash,
    )
    # Store the plain API key for testing
    brand.plain_api_key = api_key
    return brand


@pytest.fixture
def brand_wprocket(db):
    """Create a WP Rocket brand for testing."""
    api_key = "test-api-key-wprocket"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    brand = Brand.objects.create(
        name="WP Rocket",
        slug="wprocket",
        api_key_hash=api_key_hash,
    )
    brand.plain_api_key = api_key
    return brand


@pytest.fixture
def product_rankmath_pro(brand_rankmath):
    """Create a RankMath Pro product."""
    return Product.objects.create(
        brand=brand_rankmath,
        name="RankMath Pro",
        slug="rankmath-pro",
        default_seat_limit=5,
    )


@pytest.fixture
def product_content_ai(brand_rankmath):
    """Create a Content AI addon product."""
    return Product.objects.create(
        brand=brand_rankmath,
        name="Content AI",
        slug="content-ai",
        default_seat_limit=None,  # Unlimited
    )


@pytest.fixture
def product_wprocket_standard(brand_wprocket):
    """Create a WP Rocket Standard product."""
    return Product.objects.create(
        brand=brand_wprocket,
        name="WP Rocket Standard",
        slug="wprocket-standard",
        default_seat_limit=3,
    )


@pytest.fixture
def license_key_rankmath(brand_rankmath):
    """Create a license key for RankMath."""
    return LicenseKey.objects.create(
        key=f"{brand_rankmath.slug.upper()}-test-key-123",
        brand=brand_rankmath,
        customer_email="test@example.com",
    )


@pytest.fixture
def license_rankmath_pro(license_key_rankmath, product_rankmath_pro):
    """Create a valid license for RankMath Pro."""
    return License.objects.create(
        license_key=license_key_rankmath,
        product=product_rankmath_pro,
        status=License.Status.VALID,
        expires_at=timezone.now() + timezone.timedelta(days=365),
        seat_limit=5,
    )


@pytest.fixture
def activation(license_rankmath_pro):
    """Create an activation for testing."""
    return Activation.objects.create(
        license=license_rankmath_pro,
        instance_identifier="https://example.com",
        metadata={"plugin_version": "1.0.0"},
    )
