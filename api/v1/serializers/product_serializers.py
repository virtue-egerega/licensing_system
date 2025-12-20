from rest_framework import serializers

from core.models import Activation


class CreateActivationSerializer(serializers.Serializer):
    """
    Serializer for activating a license (US3).
    """

    license_key = serializers.CharField(required=True)
    instance_identifier = serializers.CharField(required=True)
    metadata = serializers.JSONField(required=False, default=dict)


class ActivationResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for activation.
    """

    license_id = serializers.UUIDField(source="license.id", read_only=True)
    product_name = serializers.CharField(source="license.product.name", read_only=True)
    license_key = serializers.CharField(
        source="license.license_key.key", read_only=True
    )

    class Meta:
        model = Activation
        fields = [
            "id",
            "license_id",
            "license_key",
            "product_name",
            "instance_identifier",
            "activated_at",
            "deactivated_at",
            "metadata",
        ]
        read_only_fields = fields


class DeactivateActivationSerializer(serializers.Serializer):
    """
    Serializer for deactivating an activation (US5).
    """

    activation_id = serializers.UUIDField(required=True)
