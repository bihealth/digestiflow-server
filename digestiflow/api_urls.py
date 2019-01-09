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
    # /sequencers/:project/
    url(
        regex=r"^sequencers/(?P<project>[0-9a-f-]+)/$",
        view=sequencer_views.SequencingMachineCreateApiView.as_view(),
        name="sequencers",
    ),
    # /sequencers/by-vendor-id/:project/:vendor_id/
    url(
        regex=r"^sequencers/by-vendor-id/(?P<project>[0-9a-f-]+)/(?P<sequencer>[^/]+)/$",
        view=sequencer_views.SequencingMachineByVendorApiView.as_view(),
        name="sequencers",
    ),
    # /sequencers/:project/:sequencer/
    url(
        regex=r"^sequencers/(?P<project>[0-9a-f-]+)/(?P<sequencer>([0-9a-f-]+))$",
        view=sequencer_views.SequencingMachineUpdateDestroyApiView.as_view(),
        name="sequencers",
    ),
    #
    # App "barcodesets"
    #
    # /barcodesets/:project/
    url(
        regex=r"^barcodesets/(?P<project>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetCreateApiView.as_view(),
        name="barcodesets",
    ),
    # /barcodesets/:project/:barcodeset/
    url(
        regex=r"^barcodesets/(?P<project>[0-9a-f-]+)/(?P<barcodeset>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetUpdateDestroyApiView.as_view(),
        name="barcodesets",
    ),
    # /barcodesetentries/:project/
    url(
        regex=r"^barcodesetentries/(?P<project>[0-9a-f-]+)/(?P<barcodeset>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetEntryCreateApiView.as_view(),
        name="barcodesetentries",
    ),
    # /barcodesetentries/:project/:barcodeset/
    url(
        regex=r"^barcodesetentries/(?P<project>[0-9a-f-]+)/(?P<barcodeset>[0-9a-f-]+)/(?P<barcodesetentry>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetEntryUpdateDestroyApiView.as_view(),
        name="barcodesetentries",
    ),
    # /barcodesetentries/retrieve/:project/:barcodesetentry/ -- WITHOUT barcode set!
    url(
        regex=r"^barcodesetentries/retrieve/(?P<project>[0-9a-f-]+)/(?P<barcodesetentry>[0-9a-f-]+)/$",
        view=barcode_views.BarcodeSetEntryRetrieveApiView.as_view(),
        name="barcodesetentries-detail",
    ),
    #
    # App "flowcells"
    #
    # /flowcells/:project/
    url(
        regex=r"^flowcells/(?P<project>[0-9a-f-]+)/$",
        view=flowcell_views.FlowCellListCreateApiView.as_view(),
        name="flowcells",
    ),
    # /flowcells/:project/:flowcell/
    url(
        regex=r"^flowcells/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.FlowCellUpdateDestroyApiView.as_view(),
        name="flowcells",
    ),
    # /flowcells/:project/resolve/:instrument/:run_no/:flowcell_id/
    url(
        regex=r"^flowcells/resolve/(?P<project>[0-9a-f-]+)/(?P<instrument_id>[^/]+)/(?P<run_no>[^/]+)/(?P<flowcell_id>[^/]+)/$",
        view=flowcell_views.FlowCellResolveApiView.as_view({"get": "resolve"}),
        name="flowcells",
    ),
    # /flowcells/:project/:flowcell/
    url(
        regex=r"^indexhistos/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramListCreateApiView.as_view(),
        name="indexhistos",
    ),
    # /indexhistos/:project/:flowcell/:indexhistogram/
    url(
        regex=r"^indexhistograms/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<indexhistogram>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramUpdateDestroyApiView.as_view(),
        name="indexhistos",
    ),
    # /indexhistos/:project/:flowcell/
    url(
        regex=r"^indexhistos/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramListCreateApiView.as_view(),
        name="libraries",
    ),
    # /indexhistos/:project/:flowcell/:library/
    url(
        regex=r"^indexhistos/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<library>[0-9a-f-]+)/$",
        view=flowcell_views.LaneIndexHistogramUpdateDestroyApiView.as_view(),
        name="indexhistos",
    ),
    # /messages/:project/:flowcell/
    url(
        regex=r"^messages/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/$",
        view=flowcell_views.MessageListCreateApiView.as_view(),
        name="messages",
    ),
    # /messages/:project/:flowcell/:message/
    url(
        regex=r"^messages/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<message>[0-9a-f-]+)/$",
        view=flowcell_views.MessageUpdateDestroyApiView.as_view(),
        name="messages",
    ),
    # /attachments/:project/:flowcell/:message/
    url(
        regex=r"^attachments/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<message>[0-9a-f-]+)/$",
        view=flowcell_views.AttachmentListApiView.as_view(),
        name="attachments",
    ),
    # /attachments/:project/:flowcell/:message/:file/
    url(
        regex=(
            r"^attachments/(?P<project>[0-9a-f-]+)/(?P<flowcell>[0-9a-f-]+)/(?P<message>[0-9a-f-]+)/"
            "(?P<file>[0-9a-f-]+)/$"
        ),
        view=flowcell_views.AttachmentRetrieveApiView.as_view(),
        name="attachments",
    ),
]
