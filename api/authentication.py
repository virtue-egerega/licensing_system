import hashlib

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from core.models import Brand


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API Key authentication for brands.
    Expects X-API-Key header with the brand's API key.
    """

    def authenticate(self, request):
        api_key = request.META.get("HTTP_X_API_KEY")

        if not api_key:
            return None

        # Hash the API key to compare with stored hash
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        try:
            brand = Brand.objects.get(api_key_hash=api_key_hash)
        except Brand.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key")

        # Return brand as user and brand itself as auth
        # We use AnonymousUser since we don't have actual Django users
        return (AnonymousUser(), brand)

    def authenticate_header(self, request):
        return "X-API-Key"
