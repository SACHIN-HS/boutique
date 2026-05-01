from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0008_fix_purchaseorder_gender_column"),
        ("products", "0004_variantgender"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorderitem",
            name="variant_style",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="purchase_order_items",
                to="products.variantstyle",
            ),
        ),
        migrations.AddField(
            model_name="purchaseorderitem",
            name="variant_gender",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="purchase_order_items",
                to="products.variantgender",
            ),
        ),
    ]

