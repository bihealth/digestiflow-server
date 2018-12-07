"""Included in ``config/urls.py`` under namespace "api"."""

from django.conf.urls import url

from sequencers.api import views as sequencer_views
from barcodes.api import views as barcode_views
from flowcells.api import views as flowcell_views

app_name = "api"

urlpatterns = [
    #
    # App "sequencers"
    #
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
    #
    # App "barcodesets"
    #
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
        regex=r"^barcodesetentries/(?P<project>[0-9a-f-]+)/(?P<barcodesetentry>[0-9a-f-]+)$",
        view=barcode_views.BarcodeSetUpdateDestroyApiView.as_view(),
        name="barcodesetentries",
    ),
    #
    # App "flowcells"
    #
    # {% url "api:flowcells" project=project.sodar_uuid %}
    url(
        regex=r"^flowcells/(?P<project>[0-9a-f-]+)/$",
        view=flowcell_views.FlowCellListCreateApiView.as_view(),
        name="flowcells",
    ),
    # {% url "api:flowcells" project=project.sodar_uuid flowcell=flowcells.sodar_uuid %}
    url(
        regex=r"^flowcells/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.FlowCellUpdateDestroyApiView.as_view(),
        name="flowcells",
    ),
    # {% url "api:flowcells" project=project.sodar_uuid flowcell=flowcells.sodar_uuid %}
    url(
        regex=r"^flowcells/(?P<project>[0-9a-f-]+)/resolve/(?P<instrument_id>.+)/(?P<run_no>.+)/(?P<flowcell_id>.+)/$",
        view=flowcell_views.FlowCellResolveApiView.as_view({"get": "resolve"}),
        name="flowcells",
    ),
    # {% url "api:indexhistos" project=project.sodar_uuid flowcell=flowcells.sodar_uuid %}
    url(
        regex=r"^indexhistos/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramListCreateApiView.as_view(),
        name="indexhistos",
    ),
    # {% url "api:indexhistos" project=project.sodar_uuid flowcells=flowcells.sodar_uuid indexhistogram=indexhistogram.sodar_uuid %}
    url(
        regex=r"^indexhistograms/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<indexhistogram>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramUpdateDestroyApiView.as_view(),
        name="indexhistos",
    ),
]
