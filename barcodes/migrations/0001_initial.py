# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-05 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [("projectroles", "0006_add_remote_projects")]

    operations = [
        migrations.CreateModel(
            name="BarcodeSet",
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
                        default=uuid.uuid4, help_text="Barcodeset SODAR UUID", unique=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Full name of the barcode adapter set", max_length=100
                    ),
                ),
                (
                    "short_name",
                    models.CharField(
                        db_index=True,
                        help_text="Short, unique identifier of barcode adapter set",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Short description of the barcode set.", null=True
                    ),
                ),
                (
                    "set_type",
                    models.CharField(
                        choices=[
                            ("generic", "generic"),
                            ("10x_genomics", "10x Genomics convention"),
                        ],
                        default="generic",
                        help_text="Type of barcode set.",
                        max_length=100,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        help_text="Project in which this objects belongs",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projectroles.Project",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="BarcodeSetEntry",
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
                        default=uuid.uuid4, help_text="Barcodeset SODAR UUID", unique=True
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=100)),
                ("sequence", models.CharField(max_length=200)),
                (
                    "barcode_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="entries",
                        to="barcodes.BarcodeSet",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
    ]
