"""
Wagtail CMS configuration for {{ project_name }}.

Import this in {{ project_name }}.py to enable Wagtail:
  from .wagtail import *  # noqa
"""

INSTALLED_APPS += [  # noqa: F405, F821
    "{{ project_name }}.wagtail.CustomWagtailConfig",
    "{{ project_name }}.wagtail.CustomWagtailAdminConfig",
    "{{ project_name }}.wagtail.CustomWagtailDocsConfig",
    "{{ project_name }}.wagtail.CustomWagtailImagesConfig",
    "{{ project_name }}.wagtail.CustomWagtailSearchConfig",
    "{{ project_name }}.wagtail.CustomWagtailSnippetsConfig",
    "{{ project_name }}.wagtail.CustomWagtailFormsConfig",
    "{{ project_name }}.wagtail.CustomWagtailRedirectsConfig",
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
