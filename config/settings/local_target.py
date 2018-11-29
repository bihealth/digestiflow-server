"""Configuration for developing the remote project feature in TARGET mode"""

from .local import *  # noqa

import socket
import os


# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Uses django-environ to accept uri format
# See: https://django-environ.readthedocs.io/en/latest/#supported-types
DATABASES['default']['NAME'] = 'sodar_core_target'
DATABASES['default']['ATOMIC_REQUESTS'] = False


# General site settings
# ------------------------------------------------------------------------------

SITE_TITLE = 'SODAR Core Target Dev Site'
SITE_SUBTITLE = env.str('SITE_SUBTITLE', 'Beta')
SITE_INSTANCE_TITLE = env.str(
    'SITE_INSTANCE_TITLE', 'SODAR Core Target Example')


# Local App Settings
# ------------------------------------------------------------------------------

PROJECTROLES_SITE_MODE = 'TARGET'

# Admin user to replace non-LDAP project owners in remote sync (for TARGET site)
PROJECTROLES_ADMIN_OWNER = 'admin_target'
