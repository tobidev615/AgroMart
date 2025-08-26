from django.apps import AppConfig


class FarmersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'farmers'

    def ready(self) -> None:
        from . import signals  # noqa: F401
        return super().ready()
