from django.conf import settings
from django.shortcuts import render
import os
import random

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


import resend
from core.logger import logger
from django.template.loader import render_to_string

resend.api_key = os.getenv("RESEND_API_KEY")




def mail_configured():
    """True when the app has a way to send email: a Resend key, or SMTP login details."""
    return bool(os.getenv("RESEND_API_KEY") or (settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD))


def otp_enabled():
    """Sign-up email codes. OTP_REQUIRED = true | false | auto (auto = on once email sending is configured)."""
    mode = str(getattr(settings, "OTP_REQUIRED", "auto")).strip().lower()
    if mode in ("true", "1", "yes", "on"):
        return True
    if mode in ("false", "0", "no", "off"):
        return False
    return mail_configured()


def send_email(html_template, context, subject, email, reply_to=None):
    """Send a branded email from support@oakboundtrust.com. Returns True if it was accepted for delivery.

    Uses Resend when RESEND_API_KEY is set, otherwise the Zoho SMTP mailbox when EMAIL_HOST_PASSWORD is set.
    """
    context = {**context, 'site_url': settings.SITE_URL}
    html_content = render_to_string(html_template, context=context)
    text_content = strip_tags(html_content)
    sender = f"Oakbound Trust Bank <{settings.DEFAULT_FROM_EMAIL}>"

    try:
        if os.getenv("RESEND_API_KEY"):
            resend.api_key = os.getenv("RESEND_API_KEY")
            params = {"from": sender, "to": [email], "subject": subject, "html": html_content, "text": text_content}
            if reply_to:
                params["reply_to"] = reply_to
            r = resend.Emails.send(params)
            logger.info(f"Email sent successfully (Resend): {r}")
            return True
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            msg = EmailMultiAlternatives(subject, text_content, from_email=sender, to=[email], reply_to=[reply_to] if reply_to else None)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info("Email sent successfully (SMTP) to %s", email)
            return True
        logger.error("Email not sent: no mail transport configured (set RESEND_API_KEY or EMAIL_HOST_PASSWORD)")
        return False
    except Exception as e:
        # Log the error but don't stop the application
        logger.error(f"Email sending failed: {e}", exc_info=True)
        return False






# 404 page not found error
def handle_not_found(request, exception):
    return render(request, 'not-found.html')


# 500 server error 
def handle_server_error(request):
    return render(request, 'server-error.html')


def create_acc_no():
    l = [34, 78, 90, 45, 89, 27, 91]
    l = random.choice(l)
    r = random.randint(110000001, 999999999)
    k = str(l) + str(r)
    return k


def create_ref():
    l = ['af45', '9rt', 'vb', 'tm7', 'x8k', 'pl', 'wr3']
    l = random.choice(l)
    r = random.randint(1100000000000, 9999999999999)
    k = str(l) + str(r)
    return k


