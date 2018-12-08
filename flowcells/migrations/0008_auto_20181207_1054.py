# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-07 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0007_auto_20181207_1028")]

    operations = [
        migrations.AlterField(
            model_name="flowcell",
            name="operator",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Sequencer Operator"
            ),
        )
    ]