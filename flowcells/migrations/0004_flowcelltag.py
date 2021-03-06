# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-08 10:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("flowcells", "0003_auto_20181214_1339"),
    ]

    operations = [
        migrations.CreateModel(
            name="FlowCellTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="WATCHING", help_text="Name of tag to be assigned", max_length=64
                    ),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, help_text="FlowCellTag SODAR UUID", unique=True
                    ),
                ),
                (
                    "flowcell",
                    models.ForeignKey(
                        help_text="FlowCell to which the tag is assigned",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tags",
                        to="flowcells.FlowCell",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User for whom the tag is assigned",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flowcell_tags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["flowcell__vendor_id", "user__username", "name"]},
        )
    ]
