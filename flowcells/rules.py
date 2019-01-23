"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


rules.add_perm("flowcells", rules.always_allow)
for model in ("flowcell", "library", "message", "laneindexhistogram"):
    rules.add_perm(
        "flowcells.view_%s" % model,
        pr_rules.is_project_owner
        | pr_rules.is_project_delegate
        | pr_rules.is_project_contributor
        | pr_rules.is_project_guest,
    )
    for action in ("add", "change", "delete"):
        rules.add_perm(
            "flowcells.%s_%s" % (action, model),
            pr_rules.is_project_owner
            | pr_rules.is_project_delegate
            | pr_rules.is_project_contributor,
        )
