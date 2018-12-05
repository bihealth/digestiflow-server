from django.conf.urls import url
from . import views

app_name = "sequencers"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sequencer/$",
        view=views.SequencingMachineListView.as_view(),
        name="sequencer-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sequencer/create$",
        view=views.SequencingMachineCreateView.as_view(),
        name="sequencer-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sequencer/(?P<sequencer>[0-9a-f-]+)/$",
        view=views.SequencingMachineDetailView.as_view(),
        name="sequencer-detail",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sequencer/(?P<sequencer>[0-9a-f-]+)/update$",
        view=views.SequencingMachineUpdateView.as_view(),
        name="sequencer-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sequencer/(?P<sequencer>[0-9a-f-]+)/delete$",
        view=views.SequencingMachineDeleteView.as_view(),
        name="sequencer-delete",
    ),
]
