from rest_framework import serializers

from core.models import License, LicenseKey, Product


class CreateLicenseKeySerializer(serializers.Serializer):
    """
    Serializer for creating a new license key for a customer.
    """

    customer_email = serializers.EmailField(required=True)


class LicenseKeyResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for license key.
    """

    class Meta:
        model = LicenseKey
        fields = ["id", "key", "customer_email", "created_at"]
        read_only_fields = fields


class CreateLicenseSerializer(serializers.Serializer):
    """
    Serializer for creating a license (US1).
    """

    customer_email = serializers.EmailField(required=True)
    product_slug = serializers.SlugField(required=True)
    license_key = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    seat_limit = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for product information.
    """

    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "brand_name", "default_seat_limit"]
        read_only_fields = fields


class LicenseResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for license with full details.
    """

    product = ProductSerializer(read_only=True)
    license_key_str = serializers.CharField(source="license_key.key", read_only=True)
    customer_email = serializers.CharField(
        source="license_key.customer_email", read_only=True
    )
    seats_used = serializers.SerializerMethodField()
    seats_total = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = [
            "id",
            "license_key_str",
            "customer_email",
            "product",
            "status",
            "expires_at",
            "seat_limit",
            "seats_used",
            "seats_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_seats_used(self, obj):
        return obj.get_active_activations_count()

    def get_seats_total(self, obj):
        return obj.get_seat_limit()


class UpdateLicenseSerializer(serializers.Serializer):
    """
    Serializer for updating license status/expiration (US2).
    """

    status = serializers.ChoiceField(
        choices=License.Status.choices, required=False, allow_null=True
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
