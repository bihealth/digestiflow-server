from mail_factory import factory
from mail_factory.mails import BaseMail


class FlowcellCreatedEmail(BaseMail):
    """Sent when a flow cell has been created"""

    template_name = "flowcell_created"
    params = ["user", "flowcell"]


class FlowcellStateChangedEmail(BaseMail):
    """Sent when a flow cell changes its state"""

    template_name = "flowcell_state_changed"
    params = ["user", "flowcell"]


class FlowcellMessageEmail(BaseMail):
    """Sent when a message is added"""

    template_name = "flowcell_message"
    params = ["user", "flowcell"]


factory.register(FlowcellCreatedEmail)
factory.register(FlowcellStateChangedEmail)
factory.register(FlowcellMessageEmail)
