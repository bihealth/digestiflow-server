from projectroles.plugins import ProjectAppPluginPoint

from digestiflow.utils import humanize_dict
from .models import FlowCell, Library, Message, MSG_STATE_SENT
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "flowcells"
    title = "Flow Cells"
    urls = urlpatterns

    icon = "flask"

    entry_point_url_id = "flowcells:flowcell-list"

    description = "Management of flow cells"

    #: Required permission for accessing the app
    app_permission = "flowcells"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["flowcell", "library", "message"]

    #: Search results template
    search_template = "flowcells/_search_results.html"

    #: App card template for the project details page
    details_template = "flowcells/_details_card.html"

    #: App card title for the project details page
    details_title = "Flow Cells"

    #: Position in plugin ordering
    plugin_ordering = 10

    def search(self, search_term, user, search_type=None, keywords=None):
        """
        Return app items based on a search term, user, optional type and optional keywords

        :param search_term: String
        :param user: User object for user initiating the search
        :param search_type: String
        :param keywords: List (optional)
        :return: Dict
        """
        items = []

        if not search_type:
            flow_cells = FlowCell.objects.find(search_term, keywords)
            libraries = Library.objects.find(search_term, keywords)
            messages = Message.objects.find(search_term, keywords).filter(state=MSG_STATE_SENT)
            items = list(flow_cells) + list(libraries) + list(messages)
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "flowcell":
            items = FlowCell.objects.find(search_term, keywords)
        elif search_type == "library":
            items = Library.objects.find(search_term, keywords)
        elif search_type == "message":
            items = Message.objects.find(search_term, keywords).filter(state=MSG_STATE_SENT)

        return {
            "all": {
                "title": "Flow Cells, Libraries and Messages",
                "search_types": ["flowcell", "library", "message"],
                "items": items,
            }
        }

    def get_extra_data_link(self, extra_data, name):
        """Return link for the given label that started with ``"extra-"``."""
        if name == "extra-flowcell_dict":
            return humanize_dict(extra_data["flowcell_dict"])
        else:
            return "(unknown %s)" % name

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: sodar_uuid of the referred object
        :return: Dict or None if not found
        """
        obj = self.get_object(eval(model_str), uuid)

        if isinstance(obj, FlowCell):
            return {"url": obj.get_absolute_url(), "label": obj.get_full_name()}
        elif isinstance(obj, Library):
            return {"url": obj.get_absolute_url(), "label": obj.name}

        return None
