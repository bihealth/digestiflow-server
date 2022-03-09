from projectroles.models import RoleAssignment, Project
from projectroles.plugins import ProjectAppPluginPoint

from digestiflow.utils import humanize_dict
from .models import BarcodeSet, BarcodeSetEntry
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "barcodes"
    title = "Barcodes"
    urls = urlpatterns

    icon = "mdi:barcode"

    entry_point_url_id = "barcodes:barcodeset-list"

    description = "Management of barcodes and barcode sets"

    #: Required permission for accessing the app
    app_permission = "barcodes"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["barcodeset", "barcodesetentry"]

    #: Search results template
    search_template = "barcodes/_search_results.html"

    #: App card template for the project details page
    details_template = "barcodes/_details_card.html"

    #: App card title for the project details page
    details_title = "Barcode Sets"

    #: Position in plugin ordering
    plugin_ordering = 11

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
            barcode_sets = BarcodeSet.objects.find(search_term, keywords).filter(
                project__in=projects
            )
            barcode_set_entries = BarcodeSetEntry.objects.find(search_term, keywords).filter(
                barcode_set__project__in=projects
            )
            items = list(barcode_sets) + list(barcode_set_entries)
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "barcodeset":
            items = BarcodeSetEntry.objects.find(search_term, keywords)
        elif search_type == "barcodesetentry":
            items = BarcodeSetEntry.objects.find(search_term, keywords)

        return {
            "all": {
                "title": "Barcodes and Barcode Sets",
                "search_types": ["barcodeset", "barcodesetentry"],
                "items": items,
            }
        }

    def get_extra_data_link(self, extra_data, name):
        """Return link for the given label that started with ``"extra-"``."""
        if name == "extra-barcodeset_dict":
            return humanize_dict(extra_data["barcodeset_dict"])
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

        if isinstance(obj, BarcodeSet):
            return {"url": obj.get_absolute_url(), "label": obj.name}
        elif isinstance(obj, BarcodeSetEntry):
            return {"url": obj.barcode_set.get_absolute_url(), "label": obj.barcode_set.name}

        return None
