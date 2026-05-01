from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0009_purchaseorderitem_item_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorderitem",
            name="reseller_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="purchaseorderitem",
            name="reseller_sku",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]

