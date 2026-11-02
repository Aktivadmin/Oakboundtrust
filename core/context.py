from django.conf import settings


def admin_view(request):
    """Expose the admin-view flags to every template."""
    return {
        "impersonating": getattr(request, "impersonating", False),
        "real_user": getattr(request, "real_user", None),
        "smartsupp_key": getattr(settings, "SMARTSUPP_KEY", ""),
    }
