from django.conf.urls import url
from . import views

app_name = "tokens"

urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/tokens/$",
        view=views.UserTokenListView.as_view(),
        name="token-list",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/tokens/create$",
        view=views.UserTokenCreateView.as_view(),
        name="token-create",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/tokens/(?P<pk>.+)/delete$",
        view=views.UserTokenDeleteView.as_view(),
        name="token-delete",
    ),
]
