"""Add ``rank`` field to ``Library`` and initialize per-flow cell."""
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    FlowCell = apps.get_model("flowcells", "FlowCell")
    for flow_cell in FlowCell.objects.all():
        for rank, library in enumerate(flow_cell.libraries.all()):
            library.rank = rank
            library.save()


def reverse_func(apps, schema_editor):
    """Do nothing, reverting the migration will drop the column anyway."""


class Migration(migrations.Migration):

    dependencies = [("flowcells", "0010_auto_20190219_0656")]

    operations = [
        migrations.AlterModelOptions(name="library", options={"ordering": ["rank", "name"]}),
        migrations.AddField(
            model_name="library",
            name="rank",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
