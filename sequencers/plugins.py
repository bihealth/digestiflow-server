from projectroles.models import RoleAssignment, Project
from projectroles.plugins import ProjectAppPluginPoint

from digestiflow.utils import humanize_dict
from .models import SequencingMachine
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "sequencers"
    title = "Sequencers"
    urls = urlpatterns

    icon = "industry"

    entry_point_url_id = "sequencers:sequencer-list"

    description = "Management of sequencing machines"

    #: Required permission for accessing the app
    app_permission = "sequencers"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["sequencing_machine"]

    #: Search results template
    search_template = "sequencers/_search_results.html"

    #: App card template for the project details page
    details_template = "sequencers/_details_card.html"

    #: App card title for the project details page
    details_title = "Sequencing Machines"

    #: Position in plugin ordering
    plugin_ordering = 12

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
            sequencers = SequencingMachine.objects.find(search_term, keywords).filter(
                project__in=projects
            )
            items = list(sequencers)
            items.sort(key=lambda x: x.vendor_id.lower())
        elif search_type == "sequencer":
            items = SequencingMachine.objects.find(search_term, keywords).filter(
                project__in=projects
            )

        return {
            "all": {
                "title": "Sequencing Machines",
                "search_types": ["sequencing_machine"],
                "items": items,
            }
        }

    def get_extra_data_link(self, extra_data, name):
        """Return link for the given label that started with ``"extra-"``."""
        if name == "extra-sequencer_dict":
            return humanize_dict(extra_data["sequencer_dict"])
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

        if isinstance(obj, SequencingMachine):
            return {"url": obj.get_absolute_url(), "label": obj.vendor_id}

        return None
