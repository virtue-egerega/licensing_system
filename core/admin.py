from django.contrib import admin

from .models import Activation, AuditLog, Brand, License, LicenseKey, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "slug", "default_seat_limit", "created_at"]
    list_filter = ["brand"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ["key", "brand", "customer_email", "created_at"]
    list_filter = ["brand"]
    search_fields = ["key", "customer_email"]
    readonly_fields = ["id", "key", "created_at", "updated_at"]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = [
        "license_key",
        "product",
        "status",
        "expires_at",
        "seat_limit",
        "created_at",
    ]
    list_filter = ["status", "product__brand"]
    search_fields = ["license_key__key", "product__name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    list_display = [
        "license",
        "instance_identifier",
        "activated_at",
        "deactivated_at",
    ]
    list_filter = ["deactivated_at"]
    search_fields = ["license__license_key__key", "instance_identifier"]
    readonly_fields = ["id", "activated_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "entity_type", "entity_id", "actor", "created_at"]
    list_filter = ["action", "entity_type", "brand"]
    search_fields = ["actor", "entity_id"]
    readonly_fields = ["id", "created_at"]
