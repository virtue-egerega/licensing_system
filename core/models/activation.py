import uuid

from django.db import models

from .license import License


class Activation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    license = models.ForeignKey(
        License, on_delete=models.CASCADE, related_name="activations"
    )
    instance_identifier = models.CharField(max_length=500)
    activated_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "activations"
        indexes = [
            models.Index(fields=["license", "deactivated_at"]),
            models.Index(fields=["instance_identifier"]),
        ]

    def __str__(self):
        status = "active" if self.deactivated_at is None else "deactivated"
        return f"{self.license.license_key.key} - {self.instance_identifier} ({status})"

    def is_active(self):
        return self.deactivated_at is None
