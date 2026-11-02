from django.db import migrations

from users import identifiers as ids


def backfill(apps, schema_editor):
    """Give every existing customer their own account, routing and card number."""
    User = apps.get_model("users", "CustomUserAccount")
    for u in User.objects.filter(account_number__isnull=True).order_by("id"):
        u.account_number = ids.unique(ids.account_number, User, "account_number")
        u.routing_number = ids.unique(ids.routing_number, User, "routing_number")
        u.card_number = ids.unique(ids.card_number, User, "card_number")
        u.save(update_fields=["account_number", "routing_number", "card_number"])


class Migration(migrations.Migration):
    dependencies = [("users", "0009_account_routing_card_numbers")]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
