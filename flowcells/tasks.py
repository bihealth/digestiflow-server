from django.db import transaction
from django.db.models import Q
from celery.schedules import crontab

from config.celery import app
from . import models


@app.task(bind=True)
def flowcell_update_error_caches(_self, flowcell_pk):
    """Update the (reverse) index and sample sheet caches of the flowcell with the given pk."""
    with transaction.atomic():
        models.FlowCell.objects.get(pk=flowcell_pk).update_error_caches().save()


@app.task(bind=True)
def flowcell_update_outdated_error_caches(_self):
    """Spawn tasks for all flow cells with missing or outdated error caches.

    Returns list of background tasks.
    """
    objects = models.FlowCell.objects.filter(
        Q(error_caches_version__isnull=True)
        | Q(error_caches_version__lt=models.FLOWCELL_ERROR_CACHE_VERSION)
    )
    result = []
    for obj in objects:
        result.append(flowcell_update_error_caches.delay(obj.pk))
    return tuple(result)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Update the error message caches hourly, if necessary.
    sender.add_periodic_task(
        schedule=crontab(hour=1, minute=11), signature=flowcell_update_outdated_error_caches.s()
    )
