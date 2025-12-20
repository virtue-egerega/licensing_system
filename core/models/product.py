import uuid

from django.db import models

from .brand import Brand


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    default_seat_limit = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        unique_together = [["brand", "slug"]]
        indexes = [
            models.Index(fields=["brand", "slug"]),
        ]

    def __str__(self):
        return f"{self.brand.name} - {self.name}"
