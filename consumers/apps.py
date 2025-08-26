from django.apps import AppConfig


class ConsumersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consumers'
    verbose_name = 'Consumer Management'
    
    def ready(self):
        """Import signals when the app is ready."""
        import consumers.signals
