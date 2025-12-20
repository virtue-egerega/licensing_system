import logging
import uuid

from django.db import transaction
from django.utils import timezone

from core.exceptions import (
    BrandNotFoundError,
    LicenseAlreadyExistsError,
    ProductNotFoundError,
)
from core.models import Brand, License, LicenseKey, Product

logger = logging.getLogger(__name__)


class LicenseService:
    """
    Service for managing license keys and licenses (US1, US2).
    """

    @staticmethod
    def generate_license_key(brand: Brand, customer_email: str) -> LicenseKey:
        """
        Generate a new license key for a customer.
        Format: BRAND_SLUG-UUID4
        """
        # Generate unique key
        key = f"{brand.slug.upper()}-{uuid.uuid4()}"

        license_key = LicenseKey.objects.create(
            key=key, brand=brand, customer_email=customer_email.lower()
        )

        logger.info(
            f"Generated license key {license_key.key} for {customer_email} (Brand: {brand.name})"
        )

        return license_key

    @staticmethod
    @transaction.atomic
    def create_license(
        brand: Brand,
        customer_email: str,
        product_slug: str,
        license_key_str: str = None,
        expires_at: timezone.datetime = None,
        seat_limit: int = None,
    ) -> License:
        """
        Create a license for a product.
        Can use existing license key or create a new one.
        """
        customer_email = customer_email.lower()

        # Get or create license key
        if license_key_str:
            try:
                license_key = LicenseKey.objects.get(
                    key=license_key_str, brand=brand, customer_email=customer_email
                )
            except LicenseKey.DoesNotExist:
                raise ValueError(
                    f"License key {license_key_str} not found for {customer_email}"
                )
        else:
            license_key = LicenseService.generate_license_key(brand, customer_email)

        # Get product
        try:
            product = Product.objects.get(slug=product_slug, brand=brand)
        except Product.DoesNotExist:
            raise ProductNotFoundError(
                f"Product {product_slug} not found for brand {brand.name}"
            )

        # Check if license already exists
        if License.objects.filter(license_key=license_key, product=product).exists():
            raise LicenseAlreadyExistsError(
                f"License already exists for {product.name} on key {license_key.key}"
            )

        # Create license
        license_obj = License.objects.create(
            license_key=license_key,
            product=product,
            status=License.Status.VALID,
            expires_at=expires_at,
            seat_limit=seat_limit,
        )

        logger.info(
            f"Created license {license_obj.id} for product {product.name} "
            f"on key {license_key.key} (customer: {customer_email})"
        )

        return license_obj

    @staticmethod
    def update_license_status(
        license_id: uuid.UUID, status: str, expires_at: timezone.datetime = None
    ) -> License:
        """
        Update license status and/or expiration (US2).
        """
        try:
            license_obj = License.objects.get(id=license_id)
        except License.DoesNotExist:
            raise ValueError(f"License {license_id} not found")

        if status:
            license_obj.status = status

        if expires_at is not None:
            license_obj.expires_at = expires_at

        license_obj.save()

        logger.info(
            f"Updated license {license_id}: status={status}, expires_at={expires_at}"
        )

        return license_obj

    @staticmethod
    def get_licenses_by_email(customer_email: str):
        """
        Get all licenses for a customer email across all brands (US6).
        """
        customer_email = customer_email.lower()

        license_keys = LicenseKey.objects.filter(
            customer_email=customer_email
        ).prefetch_related("licenses__product__brand")

        licenses = []
        for lk in license_keys:
            for license_obj in lk.licenses.all():
                licenses.append(license_obj)

        logger.info(f"Retrieved {len(licenses)} licenses for customer {customer_email}")

        return licenses
