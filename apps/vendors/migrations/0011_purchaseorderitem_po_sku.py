from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0010_purchaseorderitem_reseller_price_sku"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorderitem",
            name="po_sku",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]

