from django.db import migrations


def link_existing_transfers(apps, schema_editor):
    """Give transfers made before the receipt update the reference of their matching transaction."""
    Withdrawal = apps.get_model("app", "Withdrawal")
    Transaction = apps.get_model("app", "Transaction")
    used = set(Withdrawal.objects.exclude(ref="").values_list("ref", flat=True))
    for w in Withdrawal.objects.filter(ref="").order_by("id"):
        match = (Transaction.objects.filter(user=w.user, trans_type="Withdrawal", amount=int(round(w.amount)), creation_date=w.creation_date)
                 .exclude(ref__in=used).order_by("id").first())
        if match:
            w.ref = match.ref
            w.save(update_fields=["ref"])
            used.add(match.ref)


class Migration(migrations.Migration):
    dependencies = [("app", "0010_withdrawal_ref")]
    operations = [migrations.RunPython(link_existing_transfers, migrations.RunPython.noop)]
