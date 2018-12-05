"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


# ``sequencers.view_data`` -- Allow to view the sequencers in a project.
rules.add_perm(
    "sequencers.view_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor
    | pr_rules.is_project_guest,
)


# ``sequencers.modify_data`` -- Allow to modify the sequencers in a project.
rules.add_perm(
    "sequencers.modify_data",
    rules.is_superuser
    | pr_rules.is_project_owner
    | pr_rules.is_project_delegate
    | pr_rules.is_project_contributor,
)
