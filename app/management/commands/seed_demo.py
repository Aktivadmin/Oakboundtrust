"""Create or refresh the admin account and two clearly labelled demo customers.

    ADMIN_PASSWORD='...' python manage.py seed_demo   (optional: ADMIN_EMAIL, default admin@gmail.com)

The admin password is never stored in the code: it comes from the environment or --admin-password.
Demo customers have no usable password; open them from the admin console ("View dashboard").
"""
import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from app.models import Transaction

User = get_user_model()

DEMOS = [
    dict(email="demo.customer@oakboundtrust.test", first_name="Demo", last_name="Customer", balance=12480.50, savings=8200.00,
         pending_checking=640.00, expenses=2150.75, suspended=False,
         tx=[("Deposit", 2500, "Approved", "Sample: salary deposit", 2), ("Withdrawal", 480, "Approved", "Sample: rent transfer", 5),
             ("Deposit", 1200, "Approved", "Sample: refund", 9), ("Withdrawal", 95, "Pending", "Sample: utilities", 11),
             ("Investment", 1500, "Approved", "Sample: savings plan", 16), ("Withdrawal", 320, "Declined", "Sample: card payment", 21),
             ("Deposit", 800, "Pending", "Sample: cheque deposit", 26), ("Withdrawal", 60, "Approved", "Sample: subscription", 33)]),
    dict(email="demo.restricted@oakboundtrust.test", first_name="Demo", last_name="Restricted", balance=310.00, savings=0.0,
         pending_checking=0.0, expenses=45.20, suspended=True,
         tx=[("Deposit", 350, "Approved", "Sample: first deposit", 4), ("Withdrawal", 40, "Approved", "Sample: coffee", 7)]),
]


class Command(BaseCommand):
    help = "Create or refresh the admin account and demo customers."

    def add_arguments(self, parser):
        parser.add_argument("--admin-password", default=None)

    def handle(self, *args, **opts):
        pw = opts["admin_password"] or os.getenv("ADMIN_PASSWORD")
        if not pw:
            raise CommandError("Set ADMIN_PASSWORD or pass --admin-password.")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com").strip().lower()
        legacy = User.objects.filter(email="admin").first()          # earlier username-style account
        if legacy and not User.objects.filter(email=admin_email).exists():
            legacy.email = admin_email
            legacy.save()
        admin, created = User.objects.get_or_create(email=admin_email, defaults=dict(first_name="Site", last_name="Admin", zipcode="00000"))
        admin.set_password(pw)
        admin.is_staff = admin.is_superuser = admin.is_admin = admin.is_active = True
        admin.save()
        self.stdout.write(f"Admin account {'created' if created else 'updated'} ({admin_email}).")

        today = timezone.now().date()
        for d in DEMOS:
            u, made = User.objects.get_or_create(email=d["email"], defaults=dict(first_name=d["first_name"], last_name=d["last_name"], zipcode="00000"))
            u.first_name, u.last_name = d["first_name"], d["last_name"]
            u.balance, u.savings, u.pending_checking, u.expenses = d["balance"], d["savings"], d["pending_checking"], d["expenses"]
            u.is_suspended = d["suspended"]
            u.set_unusable_password()
            u.save()
            Transaction.objects.filter(user=u, description__startswith="Sample:").delete()
            for kind, amount, status, desc, days_ago in d["tx"]:
                Transaction.objects.create(user=u, trans_type=kind, amount=amount, status=status, description=desc, creation_date=today - timedelta(days=days_ago))
            self.stdout.write(f"Demo customer {'created' if made else 'refreshed'}: {u.email}")
