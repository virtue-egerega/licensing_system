import pytest
from rest_framework import status


@pytest.mark.django_db
class TestBrandLicenseKeyAPI:
    """Test brand license key creation endpoint (US1)."""

    def test_create_license_key(self, api_client, brand_rankmath):
        """Test creating a license key."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.post(
            "/api/v1/brands/license-keys",
            {"customer_email": "newcustomer@example.com"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "key" in response.data
        assert "RANKMATH" in response.data["key"]
        assert response.data["customer_email"] == "newcustomer@example.com"

    def test_create_license_key_unauthorized(self, api_client):
        """Test that creating license key without API key fails."""
        response = api_client.post(
            "/api/v1/brands/license-keys",
            {"customer_email": "test@example.com"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBrandLicenseAPI:
    """Test brand license creation endpoint (US1)."""

    def test_create_license(self, api_client, brand_rankmath, product_rankmath_pro):
        """Test creating a license."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.post(
            "/api/v1/brands/licenses",
            {
                "customer_email": "customer@example.com",
                "product_slug": "rankmath-pro",
                "seat_limit": 10,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["product"]["slug"] == "rankmath-pro"
        assert response.data["seats_total"] == 10
        assert "license_key_str" in response.data

    def test_create_license_with_existing_key(
        self, api_client, brand_rankmath, product_rankmath_pro, license_key_rankmath
    ):
        """Test creating a license with existing license key."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.post(
            "/api/v1/brands/licenses",
            {
                "customer_email": "test@example.com",
                "product_slug": "rankmath-pro",
                "license_key": license_key_rankmath.key,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["license_key_str"] == license_key_rankmath.key

    def test_create_license_product_not_found(self, api_client, brand_rankmath):
        """Test creating license for non-existent product."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.post(
            "/api/v1/brands/licenses",
            {
                "customer_email": "test@example.com",
                "product_slug": "non-existent",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == "PRODUCT_NOT_FOUND"


@pytest.mark.django_db
class TestListLicensesByEmailAPI:
    """Test listing licenses by email endpoint (US6)."""

    def test_list_licenses_by_email(
        self,
        api_client,
        brand_rankmath,
        brand_wprocket,
        license_rankmath_pro,
        product_wprocket_standard,
    ):
        """Test listing all licenses for an email across brands."""
        # Create a license for the same email on different brand
        from core.services import LicenseService

        LicenseService.create_license(
            brand=brand_wprocket,
            customer_email="test@example.com",
            product_slug="wprocket-standard",
        )

        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.get(
            "/api/v1/brands/licenses/search", {"customer_email": "test@example.com"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["customer_email"] == "test@example.com"
        assert len(response.data["licenses"]) == 2

    def test_list_licenses_missing_email(self, api_client, brand_rankmath):
        """Test that missing email parameter returns error."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.get("/api/v1/brands/licenses/search")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdateLicenseAPI:
    """Test updating license endpoint (US2)."""

    def test_update_license_status(
        self, api_client, brand_rankmath, license_rankmath_pro
    ):
        """Test updating license status."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        response = api_client.patch(
            f"/api/v1/brands/licenses/{license_rankmath_pro.id}",
            {"status": "suspended"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "suspended"

    def test_update_license_not_found(self, api_client, brand_rankmath):
        """Test updating non-existent license."""
        api_client.credentials(HTTP_X_API_KEY=brand_rankmath.plain_api_key)

        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = api_client.patch(
            f"/api/v1/brands/licenses/{fake_uuid}",
            {"status": "suspended"},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
