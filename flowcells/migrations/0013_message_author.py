# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-09 19:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("flowcells", "0012_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to=settings.AUTH_USER_MODEL,
            ),
        )
    ]
