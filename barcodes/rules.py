"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


rules.add_perm("barcodes", rules.always_allow)
for model in ("barcodeset", "barcodesetentry"):
    rules.add_perm(
        "barcodes.view_%s" % model,
        pr_rules.is_project_owner
        | pr_rules.is_project_delegate
        | pr_rules.is_project_contributor
        | pr_rules.is_project_guest,
    )
    for action in ("add", "change", "delete"):
        rules.add_perm(
            "barcodes.%s_%s" % (action, model),
            pr_rules.is_project_owner
            | pr_rules.is_project_delegate
            | pr_rules.is_project_contributor,
        )
