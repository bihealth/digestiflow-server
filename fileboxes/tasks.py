from django.contrib import auth
from django.db import transaction
from django.utils import timezone
from celery.schedules import crontab

from config.celery import app
from . import models


User = auth.get_user_model()


@app.task(bind=True)
def fileboxes_update_states(_self):
    """Update states based on expiry date"""
    root = User.objects.filter(is_superuser=True).order_by("pk").first()
    with transaction.atomic():
        for object in models.FileBox.objects.filter(date_expiry__lt=timezone.now()).exclude(state_meta="DELETED"):
            object.update_state_meta(root, "state_meta", "DELETED")
        for object in models.FileBox.objects.filter(date_frozen__lt=timezone.now(), state_meta="ACTIVE"):
            object.update_state_meta(root, "state_meta", "FROZEN")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Update the error message caches hourly, if necessary.
    sender.add_periodic_task(
        schedule=crontab(), signature=fileboxes_update_states.s()
    )
