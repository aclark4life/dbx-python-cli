from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.flatpages.apps import FlatPagesConfig
from django.contrib.redirects.apps import RedirectsConfig
from django.contrib.sites.apps import SitesConfig


class CustomAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL


class CustomAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL


class CustomContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL


class CustomFlatPagesConfig(FlatPagesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL


class CustomRedirectsConfig(RedirectsConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL


class CustomSitesConfig(SitesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    # default_auto_field = "django.db.models.BigAutoField"  # For PostgreSQL
