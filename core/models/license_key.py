import uuid

from django.db import models

from .brand import Brand


class LicenseKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True, db_index=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="license_keys"
    )
    customer_email = models.EmailField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "license_keys"
        indexes = [
            models.Index(fields=["customer_email"]),
            models.Index(fields=["brand", "customer_email"]),
        ]

    def __str__(self):
        return self.key
