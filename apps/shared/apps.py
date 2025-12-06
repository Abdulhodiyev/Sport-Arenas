from django.apps import AppConfig

class SharedConfig(AppConfig):
    name = "apps.shared"

    def ready(self):
        import apps.shared.signals
