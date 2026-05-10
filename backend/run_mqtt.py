import os
import time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.mqtt import start_mqtt_client  # noqa: E402


if __name__ == '__main__':
    start_mqtt_client()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
