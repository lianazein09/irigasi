import os
from django.apps import AppConfig
from django.conf import settings

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        if not getattr(settings, 'MQTT_ENABLED', True):
            return

        # In development with autoreload enabled, Django starts twice.
        # In production under Gunicorn, RUN_MAIN is usually unset, so allow startup.
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('RUN_MAIN') is None:
            from .mqtt import start_mqtt_client
            start_mqtt_client()
