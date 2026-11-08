"""Admin "view as customer" support.

A superuser can open a customer's dashboard from the admin console. While doing so
`request.user` is the customer, so every page renders exactly as they see it, but the
session stays read-only: any write request is bounced back with a message.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

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


BLOCKED_PREFIXES = ("/dashboard/", "/transactions/", "/credit_card/", "/deposit/", "/withdraw/", "/international-transfer/",
                    "/receipt/", "/beneficiary/", "/application/", "/appy-for-loan/")


class SuspensionMiddleware:
    """A suspended customer can sign in and sign out, but every account page and action shows the
    compliance-review notice instead. Admins viewing a customer's dashboard (read-only) are not affected."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if (user.is_authenticated and getattr(user, "is_suspended", False) and not getattr(request, "impersonating", False)
                and not user.is_superuser and request.path.startswith(BLOCKED_PREFIXES)):
            return render(request, "suspended.html", status=403)
        return self.get_response(request)
