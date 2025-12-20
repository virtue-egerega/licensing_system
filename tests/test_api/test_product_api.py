import pytest
from rest_framework import status


@pytest.mark.django_db
class TestActivationAPI:
    """Test activation endpoints (US3, US5)."""

    def test_activate_license(self, api_client, license_rankmath_pro):
        """Test activating a license."""
        response = api_client.post(
            "/api/v1/products/activations",
            {
                "license_key": license_rankmath_pro.license_key.key,
                "instance_identifier": "https://mysite.com",
                "metadata": {"plugin_version": "1.2.3"},
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["instance_identifier"] == "https://mysite.com"
        assert response.data["license_key"] == license_rankmath_pro.license_key.key
        assert response.data["metadata"]["plugin_version"] == "1.2.3"

    def test_activate_license_invalid_key(self, api_client):
        """Test activating with invalid license key."""
        response = api_client.post(
            "/api/v1/products/activations",
            {
                "license_key": "INVALID-KEY",
                "instance_identifier": "https://mysite.com",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == "LICENSE_NOT_FOUND"

    def test_activate_license_seat_limit(self, api_client, license_rankmath_pro):
        """Test that seat limit is enforced."""
        # Fill up all seats
        for i in range(5):
            api_client.post(
                "/api/v1/products/activations",
                {
                    "license_key": license_rankmath_pro.license_key.key,
                    "instance_identifier": f"https://site{i}.com",
                },
                format="json",
            )

        # Try to activate one more
        response = api_client.post(
            "/api/v1/products/activations",
            {
                "license_key": license_rankmath_pro.license_key.key,
                "instance_identifier": "https://onemore.com",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["error"]["code"] == "SEAT_LIMIT_REACHED"

    def test_activate_license_idempotent(self, api_client, license_rankmath_pro):
        """Test that activating same instance twice is idempotent."""
        response1 = api_client.post(
            "/api/v1/products/activations",
            {
                "license_key": license_rankmath_pro.license_key.key,
                "instance_identifier": "https://same.com",
            },
            format="json",
        )

        response2 = api_client.post(
            "/api/v1/products/activations",
            {
                "license_key": license_rankmath_pro.license_key.key,
                "instance_identifier": "https://same.com",
            },
            format="json",
        )

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response1.data["id"] == response2.data["id"]

    def test_deactivate_activation(self, api_client, activation):
        """Test deactivating an activation (US5)."""
        response = api_client.delete(f"/api/v1/products/activations/{activation.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["deactivated_at"] is not None

    def test_deactivate_activation_not_found(self, api_client):
        """Test deactivating non-existent activation."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = api_client.delete(f"/api/v1/products/activations/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == "ACTIVATION_NOT_FOUND"
