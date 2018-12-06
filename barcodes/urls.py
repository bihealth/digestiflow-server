from django.conf.urls import url
from . import views

app_name = "barcodes"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/barcodeset/$",
        view=views.BarcodeSetListView.as_view(),
        name="barcodeset-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/barcodeset/create$",
        view=views.BarcodeSetCreateView.as_view(),
        name="barcodeset-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/barcodeset/(?P<barcodeset>[0-9a-f-]+)/$",
        view=views.BarcodeSetDetailView.as_view(),
        name="barcodeset-detail",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/barcodeset/(?P<barcodeset>[0-9a-f-]+)/update$",
        view=views.BarcodeSetUpdateView.as_view(),
        name="barcodeset-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/barcodeset/(?P<barcodeset>[0-9a-f-]+)/delete$",
        view=views.BarcodeSetDeleteView.as_view(),
        name="barcodeset-delete",
    ),
]
