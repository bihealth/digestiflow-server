"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


# ``flowcells.view_data`` -- Allow to view the flow cells in a project.
rules.add_perm(
    "flowcells.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)


# ``sequencers.modify_data`` -- Allow to modify the flow cells in a project.
rules.add_perm(
    "flowcells.modify_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
