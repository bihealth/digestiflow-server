# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-07 08:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0004_auto_20181207_0733")]

    operations = [
        migrations.AddField(
            model_name="laneindexhistogram",
            name="sample_size",
            field=models.PositiveIntegerField(default=0, help_text="Number of index reads read"),
            preserve_default=False,
        )
    ]