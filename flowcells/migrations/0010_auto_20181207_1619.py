# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-07 15:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flowcells', '0009_library'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='library',
            name='barcode_set',
        ),
        migrations.RemoveField(
            model_name='library',
            name='barcode_set2',
        ),
    ]