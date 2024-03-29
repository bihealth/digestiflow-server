# Generated by Django 3.2.12 on 2022-03-09 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flowcells", "0017_auto_20200120_0855"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flowcell",
            name="cache_index_errors",
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="flowcell",
            name="cache_reverse_index_errors",
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="flowcell",
            name="cache_sample_sheet_errors",
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="laneindexhistogram",
            name="histogram",
            field=models.JSONField(help_text="The index histogram information"),
        ),
        migrations.AlterField(
            model_name="library",
            name="suppress_barcode1_not_observed_error",
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text='Suppress "index not observed" error in barcode 1 for this library.',
            ),
        ),
        migrations.AlterField(
            model_name="library",
            name="suppress_barcode2_not_observed_error",
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text='Suppress "index not observed" error in barcode 2 for this library.',
            ),
        ),
    ]
