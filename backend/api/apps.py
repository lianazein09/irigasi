import os
from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Prevent the MQTT client from starting twice in development when using auto-reloading
        if os.environ.get('RUN_MAIN') == 'true':
            from .mqtt import start_mqtt_client
            start_mqtt_client()
