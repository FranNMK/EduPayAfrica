"""Custom middleware for EduPayAfrica platform."""

from platform_admin.models import PlatformUserProfile


class PlatformUserProfileMiddleware:
    """Auto-create PlatformUserProfile for authenticated users."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            PlatformUserProfile.objects.get_or_create(user=request.user)
        return self.get_response(request)
