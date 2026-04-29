from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Конфигурация приложения задач"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
