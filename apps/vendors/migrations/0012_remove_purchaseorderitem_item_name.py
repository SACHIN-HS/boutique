from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0011_purchaseorderitem_po_sku"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaseorderitem",
            name="item_name",
        ),
    ]

