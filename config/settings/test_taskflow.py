"""
Taskflow test settings

- Used to run tests against a SODAR Taskflow instance
"""

from .test import *  # noqa


# Taskflow backend settings
TASKFLOW_TARGETS = ["irods", "sodar"]
TASKFLOW_BACKEND_HOST = env.str("TASKFLOW_BACKEND_HOST", "http://0.0.0.0")
TASKFLOW_BACKEND_PORT = env.int("TASKFLOW_BACKEND_PORT", 5005)

# Plugin settings
ENABLED_BACKEND_PLUGINS = ["taskflow", "timeline_backend", "example_backend_app"]
