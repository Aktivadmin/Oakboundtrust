from django.urls import path
from .views import *
from . import pages, console as admin_console

urlpatterns = [
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('application/', application, name="application"),
    path('beneficiary/', beneficiary, name="beneficiary"),

    path('login/', login_user, name="login"),
    path('signup/', signup, name="signup"),
    path('verify-email/', verify_email, name="verify-email"),
    path('logout/', logout_user, name="logout"),
    path('password_reset/', reset_password, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),

    path('credit_card/', credit_card, name="credit-card"),
    path('deposit/', deposit, name="deposit"),
    path('withdraw/', withdraw, name="withdraw"),
    path('receipt/<str:ref>/', receipt, name="receipt"),
    path('international-transfer/', international_transfer, name="international-transfer"),
    path('transactions/', transaction, name="transaction"),
    path('dashboard/', dashboard, name="dashboard"),

    path('mortgage/', mortgage, name="mortgage"),
    path('loans/', loans, name="loans"),
    path('appy-for-loan/', apply_for_loan, name="apply-for-loan"),
    path('small-businesses/', small_businesses, name="small-businesses"),
    path('investment/', investment, name="investment"),

    # admin console (superusers only): view a customer's dashboard, read-only
    path('console/', admin_console.console, name="console"),
    path('console/view/<int:user_id>/', admin_console.console_view, name="console-view"),
    path('console/stop/', admin_console.console_stop, name="console-stop"),

    # marketing pages
    path('cards/', pages.cards, name="cards"),
    path('pricing/', pages.pricing, name="pricing"),
    path('services/', pages.services, name="services"),
    path('security/', pages.security, name="security"),
    path('blog/', pages.blog, name="blog"),
    path('blog/<slug:slug>/', pages.blog_post, name="blog-post"),
    path('careers/', pages.careers, name="careers"),
    path('careers/<slug:slug>/', pages.career_detail, name="career-detail"),
    path('help/', pages.help_centre, name="help"),
    path('contact/', pages.contact, name="contact"),
]
