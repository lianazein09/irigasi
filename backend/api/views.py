from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.conf import settings
from pathlib import Path
import csv
import json
from datetime import datetime

from .models import TelemetryLog, SprinklerLog, Sensor

DEVICE_CACHE_PATH = Path(settings.BASE_DIR) / 'device_latest.json'
MAX_HISTORY_ITEMS = 100000


def load_device_cache():
    if not DEVICE_CACHE_PATH.exists():
        return {"latest": None, "history": []}

    try:
        cached = json.loads(DEVICE_CACHE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {"latest": None, "history": []}

    if not isinstance(cached, dict):
        return {"latest": None, "history": []}

    latest = cached.get("latest")
    history = cached.get("history")
    if not isinstance(history, list):
        history = []

    return {"latest": latest, "history": history}


def save_device_cache(payload):
    history = load_device_cache().get("history", [])
    history.append(payload)

    DEVICE_CACHE_PATH.write_text(json.dumps({
        "latest": payload,
        "history": history,
    }))


def get_or_create_sensor(jenis_sensor, satuan, device_id=1):
    sensor = Sensor.objects.filter(jenis_sensor=jenis_sensor).order_by('id_sensor').first()
    if sensor:
        return sensor

    return Sensor.objects.create(
        id_device_id=device_id,
        jenis_sensor=jenis_sensor,
        satuan=satuan,
    )


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'on'}
    return bool(value)


def build_chart_data(history):
    today = timezone.localtime().date()
    chart_data = []

    for item in history:
        timestamp_raw = item.get('timestamp')
        if not timestamp_raw:
            continue
        try:
            parsed = datetime.fromisoformat(timestamp_raw)
        except ValueError:
            continue

        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())

        local_time = timezone.localtime(parsed)
        if local_time.date() != today:
            continue

        chart_data.append({
            "time": local_time.strftime('%H:%M'),
            "kelembapan": item.get('soil_percent', 0),
            "cahaya": item.get('lux', 0),
            "suhu": item.get('temperature', 0),
            "kelembapan_udara": item.get('humidity', 0),
            "curah_hujan": item.get('rain_mm', 0),
        })

    return chart_data[-24:]


@api_view(['GET'])
def dashboard_data(request):
    try:
        latest_kelembapan = 0
        latest_cahaya = 0
        latest_suhu = 0
        latest_kelembapan_udara = 0
        latest_curah_hujan = 0
        
        kelem_sensor = Sensor.objects.filter(jenis_sensor='kelembapan').first()
        suhu_sensor = Sensor.objects.filter(jenis_sensor='suhu').first()

        if kelem_sensor:
            k_log = TelemetryLog.objects.filter(id_sensor=kelem_sensor).order_by('-timestamp').first()
            if k_log:
                latest_kelembapan = k_log.nilai_sensor
                
        if suhu_sensor:
            s_log = TelemetryLog.objects.filter(id_sensor=suhu_sensor).order_by('-timestamp').first()
            if s_log:
                latest_cahaya = s_log.nilai_sensor  # Using suhu as a substitute since light isn't in DB enum currently
        
        # Cek status pompa terakhir
        latest_pompa = SprinklerLog.objects.order_by('-waktu').first()
        pompa_aktif = False
        if latest_pompa and latest_pompa.status == 'ON':
            pompa_aktif = True

        cache = load_device_cache()
        latest_payload = cache.get("latest") or {}
        chart_data = build_chart_data(cache.get("history", []))

        device_status = "offline"

        if latest_payload:
            timestamp_raw = latest_payload.get('timestamp')
            is_active = False
            if timestamp_raw:
                try:
                    parsed_time = datetime.fromisoformat(timestamp_raw)
                    if timezone.is_naive(parsed_time):
                        parsed_time = timezone.make_aware(parsed_time, timezone.get_current_timezone())
                    
                    time_diff = timezone.now() - parsed_time
                    if time_diff <= timedelta(minutes=1):
                        is_active = True
                except ValueError:
                    pass

            if is_active:
                device_status = "online"
                latest_kelembapan = latest_payload.get('soil_percent', latest_kelembapan)
                latest_cahaya = latest_payload.get('lux', latest_cahaya)
                latest_suhu = latest_payload.get('temperature', latest_suhu)
                latest_kelembapan_udara = latest_payload.get('humidity', latest_kelembapan_udara)
                latest_curah_hujan = latest_payload.get('rain_mm', latest_curah_hujan)
                pompa_aktif = latest_payload.get('relay_state', pompa_aktif)
            else:
                latest_kelembapan = 0
                latest_cahaya = 0
                latest_suhu = 0
                latest_kelembapan_udara = 0
                latest_curah_hujan = 0
                pompa_aktif = False
        else:
            latest_kelembapan = 0
            latest_cahaya = 0
            latest_suhu = 0
            latest_kelembapan_udara = 0
            latest_curah_hujan = 0
            pompa_aktif = False

        data = {
            "kelembapan": latest_kelembapan,
            "cahaya": latest_cahaya,
            "suhu": latest_suhu,
            "kelembapan_udara": latest_kelembapan_udara,
            "curah_hujan": latest_curah_hujan,
            "pompa_aktif": pompa_aktif,
            "device_status": device_status,
            "chart_data": chart_data
        }
        
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def ingest_telemetry(request):
    try:
        expected_key = getattr(settings, 'DEVICE_API_KEY', None)
        provided_key = request.headers.get('X-Device-Key') or request.data.get('api_key')

        if expected_key and provided_key != expected_key:
            return Response({"success": False, "message": "API key tidak valid."}, status=403)

        soil_percent = float(request.data.get('soil_percent', 0))
        lux = float(request.data.get('lux', 0))
        temperature = float(request.data.get('temperature', 0))
        humidity = float(request.data.get('humidity', 0))
        rain_raw = int(request.data.get('rain_raw', 0))
        rain_mm = float(request.data.get('rain_mm', 0))
        relay_state = parse_bool(request.data.get('relay_state', False))

        payload = {
            "timestamp": timezone.now().isoformat(),
            "soil_percent": round(soil_percent, 2),
            "lux": round(lux, 2),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "rain_raw": rain_raw,
            "rain_mm": round(rain_mm, 2),
            "relay_state": relay_state,
        }

        save_device_cache(payload)

        try:
            kelembapan_sensor = get_or_create_sensor('kelembapan', '%')
            cahaya_sensor = get_or_create_sensor('suhu', 'lux')

            TelemetryLog.objects.create(
                id_sensor=kelembapan_sensor,
                nilai_sensor=payload['soil_percent'],
                timestamp=timezone.now(),
            )
            TelemetryLog.objects.create(
                id_sensor=cahaya_sensor,
                nilai_sensor=payload['lux'],
                timestamp=timezone.now(),
            )

            last_pump = SprinklerLog.objects.order_by('-waktu').first()
            expected_status = 'ON' if relay_state else 'OFF'
            if not last_pump or last_pump.status != expected_status:
                SprinklerLog.objects.create(
                    status=expected_status,
                    waktu=timezone.now(),
                    sumber='otomatis',
                )
        except Exception as db_error:
            payload["db_warning"] = str(db_error)

        return Response({
            "success": True,
            "message": "Data telemetry berhasil diterima.",
            "data": payload,
        })
    except (TypeError, ValueError):
        return Response({"success": False, "message": "Format data telemetry tidak valid."}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


from .models import User, LoginLog

@api_view(['POST'])
def login_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = User.objects.filter(username=username, password=password).first()
        
        if user:
            # Login berhasil
            try:
                LoginLog.objects.create(
                    id_user=user, 
                    waktu_login=timezone.now(), 
                    status_login='berhasil',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except Exception as log_error:
                # Jika gagal simpan log, tetap lanjutkan login
                print(f"Failed to save login log: {log_error}")
            
            return Response({
                "success": True,
                "data": {
                    "id_user": user.id_user,
                    "username": user.username,
                    "nama": user.nama,
                    "role": user.role
                }
            })
        else:
            return Response({"success": False, "message": "Username atau Password salah."}, status=401)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def register_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        nama = request.data.get('nama')
        role = request.data.get('role', 'user')  # Default jadi petani (user)

        if not username or not password or not nama:
            return Response({"success": False, "message": "Semua kolom harus diisi!"}, status=400)

        # Cek username
        if User.objects.filter(username=username).exists():
            return Response({"success": False, "message": "Username sudah digunakan!"}, status=400)

        user = User.objects.create(
            username=username,
            password=password,
            nama=nama,
            role=role
        )
        return Response({"success": True, "message": "Berhasil daftar!"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def download_report(request):
    # Default 30 hari agar data historis (misal tanggal 11) tetap ikut terunduh
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)

    cache = load_device_cache()
    history = cache.get("history", [])

    # Filter berdasarkan parameter days, simpan bersama timestamp-nya
    filtered = []
    for item in history:
        ts_raw = item.get('timestamp')
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
            if timezone.is_naive(ts):
                ts = timezone.make_aware(ts, timezone.get_current_timezone())
            if ts >= start_date:
                filtered.append((ts, item))
        except ValueError:
            continue

    # Urutkan berdasarkan timestamp ascending agar multi-hari tersusun rapi
    filtered.sort(key=lambda x: x[0])

    sprinkler_logs = SprinklerLog.objects.filter(waktu__gte=start_date).order_by('waktu')
    sprinkler_map = {}
    for log in sprinkler_logs:
        ts = log.waktu
        if timezone.is_naive(ts):
            ts = timezone.make_aware(ts, timezone.get_current_timezone())
        key = ts.strftime('%Y-%m-%d %H:%M')
        sprinkler_map[key] = 1 if log.status == 'ON' else 0

    response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="laporan_irigasi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Date Time', 'Soil %', 'Suhu (°C)', 'Hum', 'Intensitas cahaya (lux)', 'Rain (mm)', 'Pump'])

    for (local_ts, item) in filtered:
        try:
            local_time = timezone.localtime(local_ts)
            display_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
            minute_key = local_time.strftime('%Y-%m-%d %H:%M')

            soil_pct = item.get('soil_percent', 0)

            # Logika pompa: soil < 40% → pompa ON (1), soil > 60% → pompa OFF (0)
            # Jika ada log sprinkler yang cocok di menit tersebut, pakai itu.
            # Jika tidak, tentukan dari soil_percent.
            if minute_key in sprinkler_map:
                pump_status = sprinkler_map[minute_key]
            elif soil_pct < 40:
                pump_status = 1  # Tanah kering → pompa ON
            elif soil_pct > 60:
                pump_status = 0  # Tanah cukup lembap → pompa OFF
            else:
                # Zona tengah (40–60%): ikuti relay_state dari IoT
                pump_status = 1 if item.get('relay_state', False) else 0
        except Exception:
            continue

        writer.writerow([
            display_time,
            soil_pct,
            item.get('temperature', 0),
            item.get('humidity', 0),
            item.get('lux', 0),
            item.get('rain_mm', 0),
            pump_status
        ])

    return response


@api_view(['POST'])
def update_profile(request):
    try:
        id_user = request.data.get('id_user')
        nama = request.data.get('nama')
        username = request.data.get('username')
        password = request.data.get('password')

        if not id_user or not nama or not username:
            return Response({"success": False, "message": "ID User, Nama, dan Username wajib diisi!"}, status=400)

        # Cek apakah username sudah dipakai oleh orang lain
        if User.objects.filter(username=username).exclude(id_user=id_user).exists():
            return Response({"success": False, "message": "Username sudah digunakan oleh pengguna lain!"}, status=400)

        user = User.objects.filter(id_user=id_user).first()
        if not user:
            return Response({"success": False, "message": "Pengguna tidak ditemukan!"}, status=404)

        # Update field
        user.nama = nama
        user.username = username
        if password:  # Hanya update password jika diisi
            user.password = password
            
        user.save()
        
        return Response({
            "success": True, 
            "message": "Profil berhasil diperbarui!",
            "data": {
                "id_user": user.id_user,
                "username": user.username,
                "nama": user.nama,
                "role": user.role
            }
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)


from .models import Threshold

@api_view(['POST'])
def toggle_pump(request):
    try:
        # Determine current status
        latest_pompa = SprinklerLog.objects.order_by('-waktu').first()
        current_status = 'OFF'
        if latest_pompa and latest_pompa.status == 'ON':
            current_status = 'ON'
            
        # Toggle
        new_status = 'OFF' if current_status == 'ON' else 'ON'
        
        # Simpan ke SprinklerLog
        SprinklerLog.objects.create(
            status=new_status,
            waktu=timezone.now(),
            sumber='manual'
        )
        
        return Response({
            "success": True, 
            "pompa_aktif": new_status == 'ON', 
            "message": f"Pompa berhasil {'dinyalakan' if new_status == 'ON' else 'dimatikan'} secara manual!"
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET', 'POST'])
def threshold_api(request):
    try:
        # Ambil threshold pertama atau buat default
        threshold = Threshold.objects.first()
        if not threshold:
            threshold = Threshold.objects.create(batas_kelembapan=40, batas_suhu=30)
            
        if request.method == 'GET':
            return Response({
                "batas_kelembapan": threshold.batas_kelembapan,
                "batas_suhu": threshold.batas_suhu
            })
            
        elif request.method == 'POST':
            batas_kelembapan = request.data.get('batas_kelembapan')
            batas_suhu = request.data.get('batas_suhu')
            
            if batas_kelembapan is not None:
                threshold.batas_kelembapan = float(batas_kelembapan)
            if batas_suhu is not None:
                threshold.batas_suhu = float(batas_suhu)
                
            threshold.save()
            return Response({
                "success": True, 
                "message": "Ambang batas berhasil diperbarui!",
                "batas_kelembapan": threshold.batas_kelembapan,
                "batas_suhu": threshold.batas_suhu
            })
    except Exception as e:
        return Response({"error": str(e)}, status=500)
