# {{ project_name }} settings module.
# Import all base settings and add project-specific configurations here.

from .base import *  # noqa

# Add project-specific settings below
# Example:
# DEBUG = False
# ALLOWED_HOSTS = ['example.com']

# Add project-specific apps to INSTALLED_APPS
INSTALLED_APPS = (
    INSTALLED_APPS  # noqa: F405
    + [
        # Add your project-specific apps here
        # Example:
        # "myapp",
    ]
)

# QE (Queryable Encryption) environment settings
# Uncomment and modify these settings for QE environment:
#
# DEBUG = False
#
# ALLOWED_HOSTS = [
#     "localhost",
#     "127.0.0.1",
#     # Add your QE environment hosts here
# ]
#
# # QE-specific database configuration
# DATABASES = {
#     "default": {
#         "ENGINE": "django_mongodb_backend",
#         "HOST": os.getenv("MONGODB_URI"),
#         "NAME": "{{ project_name }}_qe",
#     },
# }
#
# # Disable debug toolbar in QE
# INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]  # noqa: F405
# MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]  # noqa: F405
#
# # QE-specific logging configuration
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "INFO",
#     },
# }
