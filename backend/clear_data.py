import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import TelemetryLog, SprinklerLog

print(f"Menghapus {TelemetryLog.objects.count()} data telemetry palsu dari database...")
TelemetryLog.objects.all().delete()

print(f"Menghapus {SprinklerLog.objects.count()} data riwayat pompa dari database...")
SprinklerLog.objects.all().delete()

cache_path = os.path.join(os.path.dirname(__file__), 'device_latest.json')
with open(cache_path, 'w') as f:
    json.dump({"latest": None, "history": []}, f)
print("File device_latest.json telah dikosongkan.")

print("\nBerhasil! Semua data palsu telah dihapus. Sistem sekarang siap menerima data asli dari IoT Anda.")
