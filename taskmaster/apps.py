# taskmaster/apps.py

from django.apps import AppConfig

class TaskmasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskmaster'

    def ready(self):
        import taskmaster.signals  # noqa: F401
