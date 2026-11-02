"""Email one-time codes for sign-up verification.

Rules: 6 digits, valid 10 minutes, 5 wrong tries then the code is burned, a new code at most every
45 seconds and at most 5 per hour. Only a keyed hash of the code is stored, never the code itself.
"""
import hashlib
import hmac
import os
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from core.logger import logger
from helpers.views import send_email

from .models import EmailOTP

CODE_LENGTH = 6
TTL = timedelta(minutes=10)
MAX_ATTEMPTS = 5
COOLDOWN = timedelta(seconds=45)
MAX_SENDS = 5
WINDOW = timedelta(hours=1)


def _hash(user, code):
    return hmac.new(settings.SECRET_KEY.encode(), f"{user.pk}:{code}".encode(), hashlib.sha256).hexdigest()


def mask_email(email):
    name, _, domain = email.partition("@")
    return (name[:1] + "*" * max(len(name) - 2, 1) + name[-1:] if len(name) > 2 else name[:1] + "*") + "@" + domain


def seconds_until_resend(user):
    otp = EmailOTP.objects.filter(user=user).first()
    if not otp:
        return 0
    return max(0, int((otp.last_sent_at + COOLDOWN - timezone.now()).total_seconds()))


def issue(user):
    """Create and email a fresh code. Returns 'sent', 'cooldown', 'limit' or 'failed'."""
    now = timezone.now()
    otp = EmailOTP.objects.filter(user=user).first()
    if otp:
        if now - otp.last_sent_at < COOLDOWN:
            return "cooldown"
        if now - otp.window_start > WINDOW:
            otp.window_start, otp.sent_in_window = now, 0
        if otp.sent_in_window >= MAX_SENDS:
            return "limit"
    else:
        otp = EmailOTP(user=user, window_start=now)

    code = "".join(secrets.choice("0123456789") for _ in range(CODE_LENGTH))
    otp.code_hash, otp.expires_at, otp.attempts = _hash(user, code), now + TTL, 0
    otp.last_sent_at, otp.sent_in_window = now, otp.sent_in_window + 1
    otp.save()

    if settings.DEBUG and not os.getenv("RESEND_API_KEY"):   # local testing only: show the code in the server log
        logger.info("DEBUG sign-up code for %s: %s", user.email, code)
    ok = send_email("emails/otp.html", {"name": user.first_name, "code": code, "minutes": int(TTL.total_seconds() // 60)},
                    "Your Oakbound verification code", user.email)
    if not ok:
        otp.last_sent_at = now - COOLDOWN   # let them retry straight away
        otp.save(update_fields=["last_sent_at"])
        return "failed"
    return "sent"


def check(user, code):
    """Returns 'ok', 'bad', 'expired', 'locked' or 'missing'. A correct code is consumed."""
    otp = EmailOTP.objects.filter(user=user).first()
    if not otp:
        return "missing"
    if timezone.now() > otp.expires_at:
        return "expired"
    if otp.attempts >= MAX_ATTEMPTS:
        return "locked"
    otp.attempts += 1
    otp.save(update_fields=["attempts"])
    if hmac.compare_digest(otp.code_hash, _hash(user, code)):
        otp.delete()
        return "ok"
    return "locked" if otp.attempts >= MAX_ATTEMPTS else "bad"
