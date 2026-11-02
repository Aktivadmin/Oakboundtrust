"""Admin console: list customers and open their dashboard (read-only)."""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

User = get_user_model()


def _admin_only(request):
    """Return a response if the caller is not a signed-in superuser, else None."""
    real = getattr(request, "real_user", None) or request.user
    if not real.is_authenticated:
        return redirect("login")
    if not real.is_superuser:
        return HttpResponseForbidden("Admins only.")
    return None


def console(request):
    denied = _admin_only(request)
    if denied:
        return denied
    q = request.GET.get("q", "").strip()
    users = User.objects.filter(is_superuser=False).order_by("-date_joined")
    if q:
        users = users.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    return render(request, "pages/console.html", {"customers": users[:200], "q": q, "count": users.count(), "admin": request.user})


@require_POST
def console_view(request, user_id):
    denied = _admin_only(request)
    if denied:
        return denied
    target = get_object_or_404(User, pk=user_id, is_superuser=False)
    request.session["impersonate_id"] = target.pk
    messages.info(request, f"Viewing {target.first_name} {target.last_name}'s dashboard.")
    return redirect("dashboard")


@require_POST
def console_stop(request):
    request.session.pop("impersonate_id", None)
    return redirect("console")
