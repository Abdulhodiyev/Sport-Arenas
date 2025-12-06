from django.apps import AppConfig

class ArenasConfig(AppConfig):
    name = "apps.arenas"

    def ready(self):
        import apps.arenas.signals
