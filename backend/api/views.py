from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.http import HttpResponse
import csv
from datetime import datetime

from .models import TelemetryLog, SprinklerLog, Sensor

@api_view(['GET'])
def dashboard_data(request):
    try:
        # Panggil data sensor terbaru
        latest_kelembapan = 0
        latest_cahaya = 0
        
        # Cari sensor kelembapan dan suhu (atau intensitas cahaya jika ada)
        # Sesuai dgn db: jenis_sensor enum('kelembapan','suhu')
        # Tapi di React butuh kelembapan dan intensitas cahaya, ada kemungkinan intensitas cahaya direpresentasikan "suhu" jika sensornya terbatas, kita coba cari "kelembapan" saja dulu.
        kelem_sensor = Sensor.objects.filter(jenis_sensor='kelembapan').first()
        suhu_sensor = Sensor.objects.filter(jenis_sensor='suhu').first()

        if kelem_sensor:
            k_log = TelemetryLog.objects.filter(id_sensor=kelem_sensor).order_by('-timestamp').first()
            if k_log:
                latest_kelembapan = k_log.nilai_sensor
                
        if suhu_sensor:
            s_log = TelemetryLog.objects.filter(id_sensor=suhu_sensor).order_by('-timestamp').first()
            if s_log:
                latest_cahaya = s_log.nilai_sensor # Using suhu as a substitute since light isn't in DB enum currently
        
        # Cek status pompa terakhir
        latest_pompa = SprinklerLog.objects.order_by('-waktu').first()
        pompa_aktif = False
        if latest_pompa and latest_pompa.status == 'ON':
            pompa_aktif = True

        # Kita buat chart_data mock berdasarkan data database jika ada, atau dummy seperti di React
        # Ambil data hari ini, agregasi per jam jika diperlukan
        chart_data = [
            {"time": "08:00", "kelembapan": 45, "cahaya": 800},
            {"time": "10:00", "kelembapan": 42, "cahaya": 1200},
            {"time": "12:00", "kelembapan": 38, "cahaya": 1500},
            {"time": "14:00", "kelembapan": 40, "cahaya": 1400},
            {"time": "16:00", "kelembapan": 55, "cahaya": 900},
            {"time": "18:00", "kelembapan": 60, "cahaya": 400},
        ]
        
        # Coba override chart_data dummy dengan jika ada data nyata di hari yang sama
        today = timezone.localtime().date()
        logs_today = TelemetryLog.objects.filter(timestamp__date=today).order_by('timestamp')
        
        if logs_today.exists():
            actual_chart = []
            # Sangat sederhana untuk contoh, grup berdasar jam:
            from itertools import groupby
            for hour, group in groupby(logs_today, key=lambda x: x.timestamp.strftime('%H:00')):
                logs = list(group)
                k_vals = [l.nilai_sensor for l in logs if l.id_sensor == kelem_sensor]
                c_vals = [l.nilai_sensor for l in logs if l.id_sensor == suhu_sensor]
                
                avg_k = sum(k_vals)/len(k_vals) if k_vals else 0
                avg_c = sum(c_vals)/len(c_vals) if c_vals else 0
                
                actual_chart.append({
                    "time": hour,
                    "kelembapan": round(avg_k, 1),
                    "cahaya": round(avg_c, 1) # Again using suhu to represent cahaya since enum
                })
            if len(actual_chart) > 0:
                chart_data = actual_chart

        # Kita biarkan 0 jika memang database masih kosong
        # agar ketahuan ini adalah data real, bukan data palsu.

        data = {
            "kelembapan": latest_kelembapan,
            "cahaya": latest_cahaya,
            "pompa_aktif": pompa_aktif,
            "chart_data": chart_data
        }
        
        return Response(data)
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
            # Login gagal
            # Kita bisa simpan ke LoginLog juga kalau mau, tp username gak ketemu id_user nya
            return Response({"success": False, "message": "Username atau Password salah."}, status=401)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def register_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        nama = request.data.get('nama')
        role = request.data.get('role', 'user') # Default jadi petani (user)

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
    """
    Download laporan data sensor dan sprinkler dalam format CSV
    Parameter opsional: days (default 7 hari terakhir)
    """
    try:
        # Ambil parameter days dari query string, default 7 hari
        days = int(request.GET.get('days', 7))
        
        # Hitung tanggal mulai
        start_date = timezone.now() - timedelta(days=days)
        
        # Query data telemetry logs
        telemetry_data = TelemetryLog.objects.filter(
            timestamp__gte=start_date
        ).select_related('id_sensor').order_by('timestamp')
        
        # Query data sprinkler logs
        sprinkler_data = SprinklerLog.objects.filter(
            waktu__gte=start_date
        ).order_by('waktu')
        
        # Buat response HTTP dengan header CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="laporan_irigasi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Buat writer CSV
        writer = csv.writer(response)
        
        # Header file CSV
        writer.writerow(['Laporan Sistem Irigasi Pintar'])
        writer.writerow([f'Periode: {start_date.strftime("%Y-%m-%d")} sampai {timezone.now().strftime("%Y-%m-%d")}'])
        writer.writerow([])
        
        # Header untuk data sensor
        writer.writerow(['=== DATA SENSOR ==='])
        writer.writerow(['Timestamp', 'Sensor', 'Nilai', 'Satuan'])
        
        # Tulis data sensor
        for log in telemetry_data:
            sensor_name = log.id_sensor.jenis_sensor if log.id_sensor else 'Unknown'
            satuan = log.id_sensor.satuan if log.id_sensor else ''
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                sensor_name,
                log.nilai_sensor,
                satuan
            ])
        
        writer.writerow([])
        
        # Header untuk data sprinkler
        writer.writerow(['=== DATA SPRINKLER ==='])
        writer.writerow(['Timestamp', 'Status', 'Sumber'])
        
        # Tulis data sprinkler
        for log in sprinkler_data:
            writer.writerow([
                log.waktu.strftime('%Y-%m-%d %H:%M:%S'),
                log.status,
                log.sumber
            ])
        
        writer.writerow([])
        writer.writerow(['Diekspor pada:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        return response
        
    except Exception as e:
        return Response({"error": f"Gagal generate laporan: {str(e)}"}, status=500)

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
        if password: # Hanya update password jika diisi
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
