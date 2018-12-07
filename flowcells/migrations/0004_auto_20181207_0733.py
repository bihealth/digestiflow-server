# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-07 06:33
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0003_auto_20181206_1653")]

    operations = [
        migrations.CreateModel(
            name="LaneIndexHistogram",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(auto_now_add=True, help_text="DateTime of creation"),
                ),
                (
                    "date_modified",
                    models.DateTimeField(auto_now=True, help_text="DateTime of last modification"),
                ),
                (
                    "sodar_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, help_text="Object SODAR UUID", unique=True
                    ),
                ),
                (
                    "lane",
                    models.PositiveIntegerField(help_text="The lane this information is for."),
                ),
                (
                    "read_no",
                    models.PositiveIntegerField(
                        help_text="The index read this information is for."
                    ),
                ),
                (
                    "histogram",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        help_text="The index histogram information"
                    ),
                ),
                (
                    "flowcell",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="index_histograms",
                        to="flowcells.FlowCell",
                    ),
                ),
            ],
            options={"ordering": ("flowcell", "lane", "read_no")},
        ),
        migrations.AlterUniqueTogether(
            name="laneindexhistogram", unique_together=set([("flowcell", "lane", "read_no")])
        ),
    ]
