"""Permissions configured using django-rules."""

import rules
from projectroles import rules as pr_rules


# ``tplems.access`` -- Access to the tokens app.
rules.add_perm(
    "tokens.access",
    rules.is_active
)
