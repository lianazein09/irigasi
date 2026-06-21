import json
import csv
from datetime import datetime, timedelta
import random
import math
from django.utils import timezone
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

random.seed(18)

tz = timezone.get_current_timezone()
today_start = timezone.make_aware(datetime(2026, 6, 21), tz)


def parse_csv(file_path):
    logs = []
    if not os.path.exists(file_path):
        return logs

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        try:
            header = next(reader)
        except StopIteration:
            return logs

        current_minute = None
        second_counter = 0

        for row in reader:
            if not row or len(row) < 7:
                continue

            time_str = row[0]
            try:
                if '-' in time_str:
                    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                else:
                    dt = datetime.strptime(time_str, '%d/%m/%Y %H:%M')
            except ValueError:
                continue

            if dt != current_minute:
                current_minute = dt
                second_counter = 0
            else:
                second_counter += 15
                if second_counter >= 60:
                    second_counter = 45

            dt_with_seconds = dt.replace(second=second_counter)
            aware_dt = timezone.make_aware(dt_with_seconds, tz)

            try:
                soil = float(row[1])
                suhu = float(row[2])
                hum = float(row[3])
                lux = float(row[4])
                rain = float(row[5])
                pump = True if float(row[6]) > 0 else False
            except ValueError:
                continue

            logs.append({
                "timestamp": aware_dt.isoformat(),
                "soil_percent": soil,
                "temperature": suhu,
                "humidity": hum,
                "lux": lux,
                "rain_mm": rain,
                "relay_state": pump
            })

    return logs


def parse_timestamp(ts_raw):
    dt = datetime.fromisoformat(ts_raw)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, tz)
    return dt


def get_parsed_logs(logs):
    parsed = []
    for item in logs:
        if not isinstance(item, dict):
            continue
        ts_raw = item.get('timestamp')
        if not ts_raw:
            continue
        try:
            parsed.append((parse_timestamp(ts_raw), item))
        except (TypeError, ValueError):
            continue
    return parsed


def generate_day_entries(day_date):
    current = timezone.make_aware(datetime.combine(day_date, datetime.min.time()), tz)
    entries = []

    while current.date() == day_date:
        hour = current.hour
        minute = current.minute

        base_soil = 55 + 10 * math.sin(2 * math.pi * (hour - 6) / 24)
        soil_percent = round(max(20, min(90, base_soil + random.gauss(0, 5))), 2)

        base_temp = 28 + 5 * math.sin(2 * math.pi * (hour - 8) / 24)
        temperature = round(max(22, min(38, base_temp + random.gauss(0, 1.5))), 2)

        base_hum = 70 - 15 * math.sin(2 * math.pi * (hour - 8) / 24)
        humidity = round(max(40, min(95, base_hum + random.gauss(0, 3))), 2)

        if 6 <= hour <= 18:
            base_lux = 800 * math.sin(math.pi * (hour - 6) / 12)
            lux = round(max(0, base_lux + random.gauss(0, 50)), 2)
        else:
            lux = round(max(0, random.gauss(5, 3)), 2)

        rain_chance = 0.15 if 14 <= hour <= 18 else 0.03
        if random.random() < rain_chance:
            rain_mm = round(random.uniform(0.5, 8.0), 2)
        else:
            rain_mm = 0.0

        relay_state = soil_percent < 40

        entries.append({
            "timestamp": current.isoformat(),
            "soil_percent": soil_percent,
            "temperature": temperature,
            "humidity": humidity,
            "lux": lux,
            "rain_mm": rain_mm,
            "relay_state": relay_state
        })

        current += timedelta(seconds=15)

    return entries


def fill_missing_dates(logs):
    parsed_logs = get_parsed_logs(logs)
    if not parsed_logs:
        return logs, []

    records_by_date = {}
    for ts, item in parsed_logs:
        local_date = ts.astimezone(tz).date()
        records_by_date.setdefault(local_date, []).append(ts)

    dates = sorted(records_by_date.keys())
    missing_dates = []
    current_date = dates[0]

    while current_date <= dates[-1]:
        if current_date not in records_by_date:
            missing_dates.append(current_date)
        current_date += timedelta(days=1)

    if not missing_dates:
        return logs, []

    filled_logs = list(logs)
    for day_date in missing_dates:
        filled_logs.extend(generate_day_entries(day_date))

    filled_logs.sort(key=lambda item: parse_timestamp(item['timestamp']))
    return filled_logs, missing_dates


logs1 = parse_csv(r'C:\Users\ASUS\Downloads\laporan_irigasi_20260617_141518.csv')
logs2 = parse_csv(r'C:\Users\ASUS\Downloads\laporan_irigasi_20260619_184839.csv')
all_csv_logs = logs1 + logs2

cache_path = 'device_latest.json'
existing_logs = []
if os.path.exists(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, dict):
            existing_logs = data.get("history", [])
        elif isinstance(data, list):
            existing_logs = data

existing_parsed = get_parsed_logs(existing_logs)
all_csv_parsed = get_parsed_logs(all_csv_logs)

preserve_from = today_start
if all_csv_parsed:
    csv_min = min(ts for ts, _ in all_csv_parsed)
    preserve_from = min(preserve_from, csv_min - timedelta(days=1))

filtered_existing = [item for ts, item in existing_parsed if ts >= preserve_from]

final_logs = all_csv_logs + filtered_existing
final_logs, missing_dates = fill_missing_dates(final_logs)

latest_log = final_logs[-1] if final_logs else None
cache_data = {
    "latest": latest_log,
    "history": final_logs
}

with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(cache_data, f, indent=4)

missing_label = ', '.join(day.isoformat() for day in missing_dates) if missing_dates else 'tidak ada'
print(f"Merged {len(all_csv_logs)} records from CSV and {len(filtered_existing)} recent records into device_latest.json.")
print(f"Added missing date(s): {missing_label}")
