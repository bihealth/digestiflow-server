"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules

rules.add_perm("sequencers", rules.always_allow)
rules.add_perm(
    "sequencers.view_sequencingmachine",
    pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)
for action in ("add", "change", "delete"):
    rules.add_perm(
        "sequencers.%s_sequencingmachine" % action,
        pr_rules.is_project_owner | pr_rules.is_project_delegate | pr_rules.is_project_contributor,
    )
