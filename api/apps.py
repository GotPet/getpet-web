from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import api.signals
