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


# Pages a suspended customer can still look at (the dashboard shows a "suspended" banner).
VIEW_ONLY_PREFIXES = ("/dashboard/", "/transactions/", "/credit_card/", "/receipt/")
# Anything that moves money or changes the account is blocked outright.
BLOCKED_PREFIXES = VIEW_ONLY_PREFIXES + ("/deposit/", "/withdraw/", "/international-transfer/", "/beneficiary/", "/application/", "/appy-for-loan/")


class SuspensionMiddleware:
    """A suspended customer can sign in, look around and sign out. The dashboard carries a suspended banner,
    and every transaction or account change (pages and form submissions) shows the compliance-review notice.
    Admins viewing a customer's dashboard (read-only) are not affected."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if (user.is_authenticated and getattr(user, "is_suspended", False) and not getattr(request, "impersonating", False)
                and not user.is_superuser and request.path.startswith(BLOCKED_PREFIXES)):
            view_only = request.path.startswith(VIEW_ONLY_PREFIXES) and request.method in ("GET", "HEAD")
            if not view_only:
                return render(request, "suspended.html", status=403)
        return self.get_response(request)
