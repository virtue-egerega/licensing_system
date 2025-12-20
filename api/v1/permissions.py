from rest_framework import permissions

from core.models import Brand


class IsBrandAuthenticated(permissions.BasePermission):
    """
    Permission that checks if the request is authenticated as a Brand.
    """

    def has_permission(self, request, view):
        # Check if authentication was successful and returned a Brand
        return (
            request.auth is not None
            and isinstance(request.auth, Brand)
            and request.auth.id is not None
        )
