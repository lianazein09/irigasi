import json
from datetime import datetime, timedelta
import random
import math

random.seed(42)

history = []
# Generate data dari 11 Juni sampai 18 Juni 2026 (8 hari)
# Setiap 5 menit sekali (288 data per hari)
start = datetime(2026, 6, 11, 0, 0, 0)
end = datetime(2026, 6, 18, 23, 55, 0)

current = start
while current <= end:
    hour = current.hour
    minute = current.minute

    # Simulate realistic sensor values with daily patterns
    # Soil moisture: higher in morning, drops during day, rises at night
    base_soil = 55 + 10 * math.sin(2 * math.pi * (hour - 6) / 24)
    soil_percent = round(max(20, min(90, base_soil + random.gauss(0, 5))), 2)

    # Temperature: peaks at 13-14h, lowest at 5-6h
    base_temp = 28 + 5 * math.sin(2 * math.pi * (hour - 8) / 24)
    temperature = round(max(22, min(38, base_temp + random.gauss(0, 1.5))), 2)

    # Humidity: inverse of temperature
    base_hum = 70 - 15 * math.sin(2 * math.pi * (hour - 8) / 24)
    humidity = round(max(40, min(95, base_hum + random.gauss(0, 3))), 2)

    # Light: peaks at noon, zero at night
    if 6 <= hour <= 18:
        base_lux = 800 * math.sin(math.pi * (hour - 6) / 12)
        lux = round(max(0, base_lux + random.gauss(0, 50)), 2)
    else:
        lux = round(max(0, random.gauss(5, 3)), 2)

    # Rain: occasional, more likely in afternoon (15-18h)
    rain_chance = 0.15 if 14 <= hour <= 18 else 0.03
    if random.random() < rain_chance:
        rain_mm = round(random.uniform(0.5, 8.0), 2)
    else:
        rain_mm = 0.0

    # Relay state: ON when soil < 40%
    relay_state = soil_percent < 40

    timestamp = current.strftime('%Y-%m-%dT%H:%M:%S+07:00')

    entry = {
        'timestamp': timestamp,
        'soil_percent': soil_percent,
        'lux': lux,
        'temperature': temperature,
        'humidity': humidity,
        'rain_raw': int(rain_mm * 100),
        'rain_mm': rain_mm,
        'relay_state': relay_state
    }
    history.append(entry)

    current += timedelta(minutes=5)

latest = history[-1]
data = {'latest': latest, 'history': history}

output_path = 'd:/Irigasi/backend/device_latest.json'
with open(output_path, 'w') as f:
    json.dump(data, f)

print(f"Generated {len(history)} data entries")
print(f"Date range: {history[0]['timestamp']} to {history[-1]['timestamp']}")
print(f"File saved to: {output_path}")
print(f"\nSample entry (middle):")
sample = history[len(history) // 2]
for k, v in sample.items():
    print(f"  {k}: {v}")
