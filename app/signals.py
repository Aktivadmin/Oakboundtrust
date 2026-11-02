"""Automatic transfer emails.

When a transfer's status is changed to Approved or Declined (from the Django admin or anywhere else that
saves the record), the customer is emailed straight away. The two records of one transfer, the Transaction
(shown in the customer's activity) and the Withdrawal (the bank details), are kept in step so changing
either one is enough, and the customer is only emailed once.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.logger import logger
from helpers.views import send_email

from .models import Transaction, Withdrawal

SKIP_SYNC = "_skip_status_sync"


def _money(user, amount):
    try:
        return f"{user.currency}{float(amount):,.2f}"
    except (TypeError, ValueError):
        return f"{user.currency}{amount}"


def send_transfer_status_email(tx):
    """Email the customer about an Approved or Declined transfer. Returns True if sent."""
    if tx.status not in ("Approved", "Declined") or not tx.user.email:
        return False
    w = Withdrawal.objects.filter(ref=tx.ref, user=tx.user).first() if tx.ref else None
    context = {
        "name": tx.user.first_name, "amount": _money(tx.user, tx.amount), "ref": tx.ref,
        "recipient": w.acc_name if w else "", "bank": w.bank_name if w else "", "date": tx.creation_date,
        "description": tx.description or "",
    }
    if tx.status == "Approved":
        template, subject = "emails/transfer_success.html", f"Your transfer of {context['amount']} was successful"
    else:
        template, subject = "emails/transfer_declined.html", "Your transfer was declined"
    ok = send_email(template, context, subject, tx.user.email)
    logger.info("Transfer %s email for %s (%s): %s", tx.status.lower(), tx.ref, tx.user.email, "sent" if ok else "NOT sent")
    return ok


@receiver(pre_save, sender=Transaction)
def _remember_transaction_status(sender, instance, **kwargs):
    instance._old_status = (Transaction.objects.filter(pk=instance.pk).values_list("status", flat=True).first() if instance.pk else None)


@receiver(post_save, sender=Transaction)
def _transaction_status_changed(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_status", None)
    if created or old is None or old == instance.status:
        return
    # keep the matching Withdrawal in step (queryset.update() does not fire signals, so no loop)
    if instance.ref:
        Withdrawal.objects.filter(ref=instance.ref, user=instance.user).exclude(status=instance.status).update(status=instance.status)
    if instance.trans_type == "Withdrawal":      # transfers only, not deposits
        send_transfer_status_email(instance)


@receiver(pre_save, sender=Withdrawal)
def _remember_withdrawal_status(sender, instance, **kwargs):
    instance._old_status = (Withdrawal.objects.filter(pk=instance.pk).values_list("status", flat=True).first() if instance.pk else None)


@receiver(post_save, sender=Withdrawal)
def _withdrawal_status_changed(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_status", None)
    if created or old is None or old == instance.status or not instance.ref:
        return
    tx = Transaction.objects.filter(ref=instance.ref, user=instance.user).first()
    if tx and tx.status != instance.status:
        tx.status = instance.status
        tx.save()                                  # fires the Transaction signal, which sends the one email
