from projectroles.models import RoleAssignment, Project
from projectroles.plugins import ProjectAppPluginPoint

from digestiflow.utils import humanize_dict
from .models import FileBox
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Fileboxes"""

    name = "fileboxes"
    title = "File Boxes"
    urls = urlpatterns

    icon = "truck"

    entry_point_url_id = "fileboxes:filebox-list"

    description = "Management of file boxes"

    #: Required permission for accessing the app
    app_permission = "fileboxes"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["filebox"]

    #: Search results template
    search_template = "fileboxes/_search_results.html"

    #: App card template for the project details page
    details_template = "fileboxes/_details_card.html"

    #: App card title for the project details page
    details_title = "File boxes"

    #: Position in plugin ordering
    plugin_ordering = 100

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

        if not user.is_superuser:
            projects = [a.project for a in RoleAssignment.objects.filter(user=user)]
        else:
            projects = Project.objects.all()

        if not search_type:
            file_boxes = FileBox.objects.find(search_term, keywords).filter(project__in=projects)
            items = list(file_boxes)
            items.sort(key=lambda x: x.title.lower())
        elif search_type == "filebox":
            items = FileBox.objects.find(search_term, keywords).filter(project__in=projects)

        return {
            "all": {
                "title": "File Boxes",
                "search_types": ["filebox"],
                "items": items,
            }
        }

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: sodar_uuid of the referred object
        :return: Dict or None if not found
        """
        obj = self.get_object(eval(model_str), uuid)

        if isinstance(obj, FileBox):
            return {"url": obj.get_absolute_url(), "label": obj.get_full_name()}

        return None
