from test_plus.test import TestCase

from ..templatetags import sequencers
from digestiflow.test_utils import SetupUserMixin, SetupProjectMixin
from ..tests import SetupSequencingMachineMixin


class TemplateTagsTest(SetupSequencingMachineMixin, SetupProjectMixin, SetupUserMixin, TestCase):
    """Test the template tags."""

    def testGetDetailsSequencers(self):
        result = sequencers.get_details_sequencers(self.project)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.first(), self.hiseq2000)
