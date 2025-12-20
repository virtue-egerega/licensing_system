from rest_framework import serializers


class LicenseStatusSerializer(serializers.Serializer):
    """
    Serializer for license status response (US4).
    """

    license_id = serializers.UUIDField()
    product = serializers.CharField()
    product_slug = serializers.CharField()
    status = serializers.CharField()
    expires_at = serializers.CharField(allow_null=True)
    seats_used = serializers.IntegerField()
    seats_total = serializers.IntegerField(allow_null=True)
    is_valid = serializers.BooleanField()


class LicenseStatusResponseSerializer(serializers.Serializer):
    """
    Full response serializer for license status check (US4).
    """

    license_key = serializers.CharField()
    customer_email = serializers.EmailField()
    valid = serializers.BooleanField()
    licenses = LicenseStatusSerializer(many=True)
