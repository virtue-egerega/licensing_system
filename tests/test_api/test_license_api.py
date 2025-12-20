import pytest
from rest_framework import status


@pytest.mark.django_db
class TestLicenseStatusAPI:
    """Test license status endpoint (US4)."""

    def test_get_license_status(self, api_client, license_rankmath_pro):
        """Test getting license status."""
        response = api_client.get(
            f"/api/v1/licenses/{license_rankmath_pro.license_key.key}/status"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["license_key"] == license_rankmath_pro.license_key.key
        assert response.data["customer_email"] == "test@example.com"
        assert response.data["valid"] is True
        assert len(response.data["licenses"]) == 1

        license_info = response.data["licenses"][0]
        assert license_info["product"] == "RankMath Pro"
        assert license_info["status"] == "valid"
        assert license_info["seats_total"] == 5
        assert license_info["seats_used"] == 0

    def test_get_license_status_with_activations(
        self, api_client, license_rankmath_pro
    ):
        """Test license status with some activations."""
        # Create some activations
        from core.services import ActivationService

        ActivationService.activate_license(
            license_key_str=license_rankmath_pro.license_key.key,
            instance_identifier="https://site1.com",
        )
        ActivationService.activate_license(
            license_key_str=license_rankmath_pro.license_key.key,
            instance_identifier="https://site2.com",
        )

        response = api_client.get(
            f"/api/v1/licenses/{license_rankmath_pro.license_key.key}/status"
        )

        assert response.status_code == status.HTTP_200_OK
        license_info = response.data["licenses"][0]
        assert license_info["seats_used"] == 2
        assert license_info["seats_total"] == 5

    def test_get_license_status_not_found(self, api_client):
        """Test getting status for non-existent license key."""
        response = api_client.get("/api/v1/licenses/INVALID-KEY/status")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == "LICENSE_NOT_FOUND"

    def test_get_license_status_multiple_products(
        self, api_client, license_key_rankmath, product_rankmath_pro, product_content_ai
    ):
        """Test license status with multiple products on same key."""
        from core.models import License

        # Create licenses for both products
        License.objects.create(
            license_key=license_key_rankmath,
            product=product_rankmath_pro,
            status=License.Status.VALID,
            seat_limit=5,
        )
        License.objects.create(
            license_key=license_key_rankmath,
            product=product_content_ai,
            status=License.Status.VALID,
            seat_limit=None,  # Unlimited
        )

        response = api_client.get(f"/api/v1/licenses/{license_key_rankmath.key}/status")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["licenses"]) == 2

        # Check that both products are present
        product_names = [lic["product"] for lic in response.data["licenses"]]
        assert "RankMath Pro" in product_names
        assert "Content AI" in product_names
