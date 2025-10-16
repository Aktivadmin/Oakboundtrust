from django.conf import settings
from django.shortcuts import render
import random


import resend
from core.logger import logger
from django.template.loader import render_to_string

resend.api_key = "RESEND_API_KEY_REMOVED"




def send_email(html_template, context, subject, email):
    # Render the HTML version
    html_content = render_to_string(html_template, context=context)
    # Optionally create a plain text fallback by stripping tags
    text_content = render_to_string(html_template, context=context)

    try:
        r = resend.Emails.send({
            "from": f"MetroCap PLC <{settings.EMAIL_HOST_USER}>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        })
        logger.info(f"Email sent successfully: {r}")
    except Exception as e:
        # Log the error but don't stop the application
        logger.error(f"Email sending failed: {e}", exc_info=True)

    return None



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


