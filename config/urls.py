from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render
from django.views import defaults as default_views
from django.views.generic import TemplateView

from projectroles.views import HomeView
from sentry_sdk import last_event_id


def handler500(request, *args, **argv):
    return render(request, "500.html", {"sentry_event_id": last_event_id()}, status=500)


urlpatterns = [
    url(r"^$", HomeView.as_view(), name="home"),
    url(r"^about/$", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    # Login and logout
    url(r"^login/$", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    url(r"^logout/$", auth_views.logout_then_login, name="logout"),
    # Auth
    url(r"api/auth/", include("knox.urls")),
    # Iconify SVG icons
    url(r"icons/", include("dj_iconify.urls")),
    ## SODAR Core
    # Projectroles URLs
    url(r"^project/", include("projectroles.urls")),
    # Filesfolders URLs
    url(r"^filesfolders/", include("filesfolders.urls")),
    # django-db-file-storage URLs (needed for admin, obfuscated for users)
    url(r"^xu7in5zs9lylar0n/", include("db_file_storage.urls")),
    # Timeline URLs
    url(r"^timeline/", include("timeline.urls")),
    # User Profile URLs
    url(r"^user/", include("userprofile.urls")),
    # Admin Alerts URLs
    url(r"^alerts/", include("adminalerts.urls")),
    # Background jobs URLs
    url(r"^bgjobs/", include("bgjobs.urls")),
    ## Local Apps
    url(r"^sequencers/", include("sequencers.urls")),
    url(r"^barcodes/", include("barcodes.urls")),
    url(r"^flowcells/", include("flowcells.urls")),
    url(r"^tokens/", include("tokens.urls")),
    ## Local Apps API
    url(r"^api/", include("digestiflow.api_urls")),
    # The rendered Sphinx-based manual.
    url(r"^manual/", include("docs.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.FILEBOXES_ENABLED:
    urlpatterns += [
        url(r"fileboxes/", include("fileboxes.urls")),
    ]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r"^400/$", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        url(
            r"^403/$",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        url(
            r"^404/$",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        url(r"^500/$", default_views.server_error),
    ]

    urlpatterns += staticfiles_urlpatterns()

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
