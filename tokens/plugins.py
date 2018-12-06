from projectroles.plugins import ProjectAppPluginPoint

from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "tokens"
    title = "API Tokens"
    urls = urlpatterns

    icon = "key"

    entry_point_url_id = "tokens:token-list"

    description = "Token Management"

    #: Required permission for accessing the app
    app_permission = "tokens.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: Position in plugin ordering
    plugin_ordering = 100
