# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-09-26 11:37
from __future__ import unicode_literals

from django.db import migrations, models
import flowcells.models


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0015_auto_20190418_1516")]

    operations = [
        migrations.AlterField(
            model_name="flowcell",
            name="current_reads",
            field=models.CharField(
                blank=True,
                help_text="Specification of the current reads",
                max_length=200,
                null=True,
                validators=[flowcells.models.validate_bases_mask],
            ),
        ),
        migrations.AlterField(
            model_name="flowcell",
            name="demux_reads",
            field=models.CharField(
                blank=True,
                help_text="Specification of the reads to use for demultiplexing (defaults to planned reads)",
                max_length=200,
                null=True,
                validators=[flowcells.models.validate_bases_mask],
            ),
        ),
        migrations.AlterField(
            model_name="flowcell",
            name="planned_reads",
            field=models.CharField(
                blank=True,
                help_text="Specification of the planned reads",
                max_length=200,
                null=True,
                validators=[flowcells.models.validate_bases_mask],
            ),
        ),
    ]
