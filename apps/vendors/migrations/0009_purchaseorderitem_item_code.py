from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0008_purchaseorderitem_style_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorderitem",
            name="item_code",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

