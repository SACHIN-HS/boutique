from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0012_remove_purchaseorderitem_item_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="purchaseorderitem",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]

