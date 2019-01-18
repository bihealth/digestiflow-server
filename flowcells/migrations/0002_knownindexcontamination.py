# -*- coding: utf-8 -*-
"""Create KnownIndexContamination model and fill with factory defaults."""

from __future__ import unicode_literals

from django.db import migrations, models
import uuid


def forwards_func(apps, schema_editor):
    KnownIndexContamination = apps.get_model("flowcells", "KnownIndexContamination")
    db_alias = schema_editor.connection.alias
    KnownIndexContamination.objects.using(db_alias).bulk_create(
        [
            KnownIndexContamination(
                title="i5 phix sequence",
                sequence="AGATCTCG",
                description=(
                    """Sometimes seen in i5 reads, PhiX sequence, index library. """
                    """Also see [Illumina index sequencing – where is my sample?]"""
                    """(http://enseqlopedia.com/2018/01/illumina-index-sequencing-sample/) on Enseqlpedia."""
                ),
                factory_default=True,
            ),
            KnownIndexContamination(
                title="i7 phix sequence",
                sequence="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                description=(
                    """Sometimes seen in i7 reads, adapter does not properly bind to PhiX. """
                    """Also see [Illumina index sequencing – where is my sample?]"""
                    """(http://enseqlopedia.com/2018/01/illumina-index-sequencing-sample/) on Enseqlpedia."""
                ),
                factory_default=True,
            ),
            KnownIndexContamination(
                title="i5 single-index contamination",
                sequence="NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN",
                description=(
                    """Sometimes seen in i5 reads of a dual indexing library that is "contamined" with a single """
                    """index library. Also see [Illumina index sequencing – where is my sample?]"""
                    """(http://enseqlopedia.com/2018/01/illumina-index-sequencing-sample/) on Enseqlpedia."""
                ),
                factory_default=True,
            ),
            KnownIndexContamination(
                title="i7 single-index contamination",
                sequence="TCTTTCCC",
                description=(
                    """Sometimes seen in i7 reads of a dual indexing library that is "contamined" with a single """
                    """index library. Also see [Illumina index sequencing – where is my sample?]"""
                    """(http://enseqlopedia.com/2018/01/illumina-index-sequencing-sample/) on Enseqlpedia."""
                ),
                factory_default=True,
            ),
            KnownIndexContamination(
                title="2-color chemistry no signal",
                sequence="GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
                description=(
                    """Illumina 2 color chemistry cannot distinguish between all-guanine sequence and "no signal"."""
                ),
                factory_default=True,
            ),
        ]
    )


def reverse_func(apps, schema_editor):
    """Do nothing, reverting the migration will drop the table anyway."""


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="KnownIndexContamination",
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
                ("title", models.CharField(max_length=200)),
                ("sequence", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "factory_default",
                    models.BooleanField(default=False, help_text="Is immutable factory default"),
                ),
            ],
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
