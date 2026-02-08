from django.apps import AppConfig


class DemoConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "{{ app_name }}"
