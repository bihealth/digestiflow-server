from django.conf.urls import url
from . import views

app_name = "fileboxes"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/$",
        view=views.FileBoxListView.as_view(),
        name="filebox-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/create$",
        view=views.FileBoxCreateView.as_view(),
        name="filebox-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/(?P<filebox>[0-9a-f-]+)/$",
        view=views.FileBoxDetailView.as_view(),
        name="filebox-detail",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/(?P<filebox>[0-9a-f-]+)/update/$",
        view=views.FileBoxUpdateView.as_view(),
        name="filebox-update",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/(?P<filebox>[0-9a-f-]+)/delete/$",
        view=views.FileBoxDeleteView.as_view(),
        name="filebox-delete",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/(?P<filebox>[0-9a-f-]+)/grant/$",
        view=views.FileBoxGrantView.as_view(),
        name="filebox-grant",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/filebox/(?P<filebox>[0-9a-f-]+)/revoke/$",
        view=views.FileBoxRevokeView.as_view(),
        name="filebox-revoke",
    ),
]
