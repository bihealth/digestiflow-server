# Generated by Django 3.2.12 on 2022-03-09 10:20

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("barcodes", "0004_auto_20190226_1209"),
    ]

    operations = [
        migrations.AlterField(
            model_name="barcodesetentry",
            name="aliases",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(db_index=True, max_length=100), default=list, size=None
            ),
        ),
    ]
