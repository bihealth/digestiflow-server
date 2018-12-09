from django.conf.urls import url
from . import views

app_name = "flowcells"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/flowcell/$",
        view=views.FlowCellListView.as_view(),
        name="flowcell-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/flowcell/create$",
        view=views.FlowCellCreateView.as_view(),
        name="flowcell-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/flowcell/(?P<flowcell>[0-9a-f-]+)/$",
        view=views.FlowCellDetailView.as_view(),
        name="flowcell-detail",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/flowcell/(?P<flowcell>[0-9a-f-]+)/update/$",
        view=views.FlowCellUpdateView.as_view(),
        name="flowcell-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/flowcell/(?P<flowcell>[0-9a-f-]+)/delete/$",
        view=views.FlowCellDeleteView.as_view(),
        name="flowcell-delete",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/message/(?P<flowcell>[0-9a-f-]+)/create/$",
        view=views.MessageCreateView.as_view(),
        name="message-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/message/(?P<flowcell>[0-9a-f-]+)/update/(?P<message>[0-9a-f-]+)/$",
        view=views.MessageUpdateView.as_view(),
        name="message-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/message/(?P<flowcell>[0-9a-f-]+)/delete/(?P<message>[0-9a-f-]+)/$",
        view=views.MessageDeleteView.as_view(),
        name="message-delete",
    ),
]
