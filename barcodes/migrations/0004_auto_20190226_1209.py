"""Add ``rank`` field to ``BarcodeSetEntry`` and initialize per barcode set."""
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


def forwards_func(apps, schema_editor):
    BarcodeSet = apps.get_model("barcodes", "BarcodeSet")
    for barcode_set in BarcodeSet.objects.all():
        for rank, entry in enumerate(barcode_set.entries.all()):
            entry.rank = rank
            entry.save()


def reverse_func(apps, schema_editor):
    """Do nothing, reverting the migration will drop the column anyway."""


class Migration(migrations.Migration):

    dependencies = [("barcodes", "0003_auto_20181211_1432")]

    operations = [
        migrations.AlterModelOptions(
            name="barcodesetentry", options={"ordering": ["barcode_set", "rank", "name"]}
        ),
        migrations.AddField(
            model_name="barcodesetentry",
            name="aliases",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(db_index=True, max_length=100), default=[], size=None
            ),
        ),
        migrations.AddField(
            model_name="barcodesetentry",
            name="rank",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
