"""Admin "view as customer" support.

A superuser can open a customer's dashboard from the admin console. While doing so
`request.user` is the customer, so every page renders exactly as they see it, but the
session stays read-only: any write request is bounced back with a message.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
SKIP_PREFIXES = ("/admin/", "/console/", "/static/")


class ImpersonationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.impersonating = False
        request.real_user = None
        uid = request.session.get("impersonate_id")
        if uid:
            user = request.user
            if not (user.is_authenticated and user.is_superuser):
                request.session.pop("impersonate_id", None)
            elif not request.path.startswith(SKIP_PREFIXES):
                target = get_user_model().objects.filter(pk=uid, is_superuser=False).first()
                if target is None:
                    request.session.pop("impersonate_id", None)
                else:
                    request.real_user, request.user, request.impersonating = user, target, True
                    if request.method not in SAFE_METHODS:
                        messages.warning(request, "Admin view is read-only. Exit the view to make changes.")
                        return redirect(request.META.get("HTTP_REFERER") or "/dashboard/")
        return self.get_response(request)
