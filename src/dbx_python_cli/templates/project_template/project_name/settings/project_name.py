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
