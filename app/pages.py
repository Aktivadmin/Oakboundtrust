"""Public marketing pages: pricing, cards, services, blog, careers, help, contact, security."""
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from core.logger import logger
from helpers.views import send_email

from . import content


def cards(request):
    return render(request, "pages/cards.html")


def pricing(request):
    return render(request, "pages/pricing.html", {"plans": content.PLANS, "faqs": content.FAQS[:4]})


def services(request):
    return render(request, "pages/services.html", {"services": content.SERVICES})


def security(request):
    return render(request, "pages/security.html")


def blog(request):
    return render(request, "pages/blog.html", {"posts": content.BLOG_POSTS})


def blog_post(request, slug):
    post = content.post_by_slug(slug)
    if not post:
        raise Http404("Article not found")
    more = [p for p in content.BLOG_POSTS if p["slug"] != slug][:3]
    return render(request, "pages/blog_post.html", {"post": post, "more": more})


def careers(request):
    return render(request, "pages/careers.html", {"jobs": content.JOBS})


def career_detail(request, slug):
    job = content.job_by_slug(slug)
    if not job:
        raise Http404("Role not found")
    return render(request, "pages/career_detail.html", {"job": job})


def help_centre(request):
    groups = {}
    for cat, q, a in content.FAQS:
        groups.setdefault(cat, []).append((q, a))
    return render(request, "pages/help.html", {"groups": groups})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        topic = request.POST.get("topic", "General").strip()
        text = request.POST.get("message", "").strip()
        if not (name and email and text):
            messages.error(request, "Please fill in your name, email and message.")
            return render(request, "pages/contact.html", {"form": request.POST})
        logger.info("Contact form: %s <%s> [%s] %s", name, email, topic, text[:500])
        try:
            send_email("emails/contact.html",
                       {"name": name, "email": email, "topic": topic, "message": text},
                       f"New message: {topic}", settings.SUPPORT_EMAIL, reply_to=email)
        except Exception as exc:  # never break the page over an email problem
            logger.error("Contact email failed: %s", exc)
        messages.success(request, "Thanks. Your message is with our team and we will reply by email.")
        return redirect("contact")
    return render(request, "pages/contact.html", {"form": {}})
