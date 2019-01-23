# -*- coding: utf-8 -*-
"""Add contamination ``"CCTTTCCC"``"""
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    KnownIndexContamination = apps.get_model("flowcells", "KnownIndexContamination")
    db_alias = schema_editor.connection.alias
    KnownIndexContamination.objects.using(db_alias).bulk_create(
        [
            KnownIndexContamination(
                title="i7 single-index contamination #2",
                sequence="CCTTTCCC",
                description=(
                    """Sometimes seen in i7 reads of a dual indexing library that is "contamined" with a single """
                    """index library (plus a T>C read error in the first base). Also see [Illumina index """
                    """sequencing – where is my sample?] """
                    """"(http://enseqlopedia.com/2018/01/illumina-index-sequencing-sample/) on Enseqlpedia."""
                ),
                factory_default=True,
            )
        ]
    )


def reverse_func(apps, schema_editor):
    """Remove sequence again"""
    KnownIndexContamination = apps.get_model("flowcells", "KnownIndexContamination")
    db_alias = schema_editor.connection.alias
    KnownIndexContamination.objects.using(db_alias).filter(sequence="CCTTTCCC").delete()


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0005_auto_20190121_1559")]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
