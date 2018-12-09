# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-09 21:41
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0015_auto_20181209_2153")]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="tags",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), blank=True, default=list, size=None
            ),
        )
    ]
