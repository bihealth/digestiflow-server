from ..models import SequencingMachine, MACHINE_MODEL_HISEQ2000, INDEX_WORKFLOW_A


class SetupSequencingMachineMixin:
    def setUp(self):
        super().setUp()
        self.hiseq2000 = SequencingMachine.objects.create(
            project=self.project,
            vendor_id="Hxxxxxxxx",
            label="Test machine",
            machine_model=MACHINE_MODEL_HISEQ2000,
            slot_count=2,
            dual_index_workflow=INDEX_WORKFLOW_A,
        )
        # Additional data for posting to API
        self.post_data = {
            "vendor_id": "Hbbbbbbb",
            "label": "API created machine",
            "machine_model": MACHINE_MODEL_HISEQ2000,
            "slot_count": 2,
            "dual_index_workflow": INDEX_WORKFLOW_A,
        }

    def make_machine(self):
        return SequencingMachine.objects.create(
            project=self.project,
            vendor_id="Hyyyyyyyy",
            label="Another test machine",
            description="This is to be found",
            machine_model=MACHINE_MODEL_HISEQ2000,
            slot_count=2,
            dual_index_workflow=INDEX_WORKFLOW_A,
        )
