"""
Wagtail CMS configuration for {{ project_name }}.

Import this in {{ project_name }}.py to enable Wagtail:
  from .wagtail import *  # noqa
"""

INSTALLED_APPS += [  # noqa: F405, F821
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailAdminConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailDocsConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailImagesConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailSearchConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailSnippetsConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailFormsConfig",
    "{{ project_name }}.settings.apps.wagtail.CustomWagtailRedirectsConfig",
    "wagtail.embeds",
    "modelcluster",
    "taggit",
]

MIDDLEWARE += [  # noqa: F405, F821
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

WAGTAIL_SITE_NAME = "{{ project_name }}"

WAGTAILADMIN_BASE_URL = "http://localhost:8000"

MEDIA_ROOT = base_dir / "media"  # noqa: F405, F821
MEDIA_URL = "/media/"
