"""
Custom app configurations for {{ project_name }}.

Note: default_auto_field is set in mongodb.py or postgresql.py settings.
These custom configs allow for database-specific customization if needed.
"""

from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.flatpages.apps import FlatPagesConfig
from django.contrib.redirects.apps import RedirectsConfig
from django.contrib.sites.apps import SitesConfig


class CustomAdminConfig(AdminConfig):
    pass


class CustomAuthConfig(AuthConfig):
    pass


class CustomContentTypesConfig(ContentTypesConfig):
    pass


class CustomFlatPagesConfig(FlatPagesConfig):
    pass


class CustomRedirectsConfig(RedirectsConfig):
    pass


class CustomSitesConfig(SitesConfig):
    pass
