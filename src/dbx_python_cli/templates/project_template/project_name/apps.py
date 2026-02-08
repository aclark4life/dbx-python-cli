from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.flatpages.apps import FlatPagesConfig
from django.contrib.redirects.apps import RedirectsConfig
from django.contrib.sites.apps import SitesConfig


class MongoDBAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDBAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDBContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDBFlatPagesConfig(FlatPagesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDBRedirectsConfig(RedirectsConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoDBSitesConfig(SitesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
