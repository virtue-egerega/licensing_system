import uuid

from django.db import models
from django.utils import timezone

from .license_key import LicenseKey
from .product import Product


class License(models.Model):
    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    license_key = models.ForeignKey(
        LicenseKey, on_delete=models.CASCADE, related_name="licenses"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="licenses"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.VALID
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    seat_limit = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "licenses"
        unique_together = [["license_key", "product"]]
        indexes = [
            models.Index(fields=["license_key", "status"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.license_key.key} - {self.product.name}"

    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def is_valid(self):
        return self.status == self.Status.VALID and not self.is_expired()

    def get_seat_limit(self):
        if self.seat_limit is not None:
            return self.seat_limit
        if self.product.default_seat_limit is not None:
            return self.product.default_seat_limit
        return None

    def get_active_activations_count(self):
        return self.activations.filter(deactivated_at__isnull=True).count()

    def has_available_seats(self):
        seat_limit = self.get_seat_limit()
        if seat_limit is None:
            return True
        return self.get_active_activations_count() < seat_limit
