from django.db import migrations


class Migration(migrations.Migration):
    """
    Historical migration present in the production DB.

    The database already reflects the intended schema; keep this migration
    as a no-op to preserve the recorded migration history.
    """

    dependencies = [
        ("vendors", "0007_purchaseorder_variant_style_vendor_gender"),
    ]

    operations = []

