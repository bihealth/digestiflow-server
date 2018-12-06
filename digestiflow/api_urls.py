"""Included in ``config/urls.py`` under namespace "api"."""

from django.conf.urls import url

from sequencers.api import views as sequencer_views
from barcodes.api import views as barcode_views

app_name = "api"

urlpatterns = [
    # {% url "api:sequencers" project=project.sodar_uuid %}
    url(
        regex=r"^sequencers/(?P<project>[0-9a-f-]+)/$",
        view=sequencer_views.SequencingMachineCreateApiView.as_view(),
        name="sequencers",
    ),
    # {% url "api:sequencers" project=project.sodar_uuid sequencer=sequencer.sodar_uuid %}
    url(
        regex=r"^sequencers/(?P<project>[0-9a-f-]+)/(?P<sequencer>(-\w]+/))$",
        view=sequencer_views.SequencingMachineUpdateDestroyApiView.as_view(),
        name="sequencers",
    ),
    # {% url "api:barcodesets" project=project.sodar_uuid %}
    url(
        regex=r"^barcodesets/(?P<project>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetCreateApiView.as_view(),
        name="barcodesets",
    ),
    # {% url "api:barcodesets" project=project.sodar_uuid barcodeset=barcodeset.sodar_uuid %}
    url(
        regex=r"^barcodesets/(?P<project>[0-9a-f-]+)/(?P<barcodeset>(-\w]+/))$",
        view=barcode_views.BarcodeSetUpdateDestroyApiView.as_view(),
        name="barcodesets",
    ),
    # {% url "api:barcodesetentries" project=project.sodar_uuid %}
    url(
        regex=r"^barcodesetentries/(?P<project>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetCreateApiView.as_view(),
        name="barcodesetentries",
    ),
    # {% url "api:barcodesetentries" project=project.sodar_uuid barcodesetentry=barcodesetentry.sodar_uuid %}
    url(
        regex=r"^barcodesetentries/(?P<project>[0-9a-f-]+)/(?P<barcodesetentry>(-\w]+/))$",
        view=barcode_views.BarcodeSetUpdateDestroyApiView.as_view(),
        name="barcodesetentries",
    ),
]
