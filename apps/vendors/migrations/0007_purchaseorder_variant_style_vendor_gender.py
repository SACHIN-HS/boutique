from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0006_alter_purchaseorder_status_and_more"),
        ("products", "0003_variantstyle"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="variant_style",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="purchase_orders",
                to="products.variantstyle",
            ),
        ),
        migrations.AddField(
            model_name="vendor",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("Men", "Men"), ("Women", "Women"), ("Kids", "Kids")],
                default="",
                max_length=10,
            ),
        ),
    ]

