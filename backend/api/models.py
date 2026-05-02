from django.db import models

class Device(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'aktif'),
        ('nonaktif', 'nonaktif'),
    ]
    id_device = models.AutoField(primary_key=True)
    nama_device = models.CharField(max_length=100, blank=True, null=True)
    lokasi_lahan = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'devices'

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('user', 'user'),
    ]
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    nama = models.CharField(max_length=100)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'users'

class DailyReport(models.Model):
    id_report = models.AutoField(primary_key=True)
    tanggal = models.DateField(blank=True, null=True)
    rata_kelembapan = models.FloatField(blank=True, null=True)
    intensitas_cahaya = models.FloatField(blank=True, null=True)
    rata_suhu = models.FloatField(blank=True, null=True)
    total_penyiraman = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_reports'

class LoginLog(models.Model):
    STATUS_CHOICES = [
        ('berhasil', 'berhasil'),
        ('gagal', 'gagal'),
    ]
    id_log = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    waktu_login = models.DateTimeField(blank=True, null=True)
    status_login = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login_logs'

class Schedule(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'aktif'),
        ('nonaktif', 'nonaktif'),
    ]
    id_schedule = models.AutoField(primary_key=True)
    waktu_mulai = models.TimeField(blank=True, null=True)
    durasi = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schedules'

class Sensor(models.Model):
    JENIS_CHOICES = [
        ('kelembapan', 'kelembapan'),
        ('suhu', 'suhu'),
    ]
    id_sensor = models.AutoField(primary_key=True)
    id_device = models.ForeignKey(Device, models.DO_NOTHING, db_column='id_device', blank=True, null=True)
    jenis_sensor = models.CharField(max_length=10, choices=JENIS_CHOICES, blank=True, null=True)
    satuan = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensors'

class SprinklerLog(models.Model):
    STATUS_CHOICES = [
        ('ON', 'ON'),
        ('OFF', 'OFF'),
    ]
    SUMBER_CHOICES = [
        ('manual', 'manual'),
        ('otomatis', 'otomatis'),
    ]
    id_log = models.AutoField(primary_key=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=True, null=True)
    waktu = models.DateTimeField(blank=True, null=True)
    sumber = models.CharField(max_length=8, choices=SUMBER_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sprinkler_logs'

class TelemetryLog(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_sensor = models.ForeignKey(Sensor, models.DO_NOTHING, db_column='id_sensor', blank=True, null=True)
    nilai_sensor = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'telemetry_logs'

class Threshold(models.Model):
    id_threshold = models.AutoField(primary_key=True)
    batas_kelembapan = models.FloatField(blank=True, null=True)
    batas_suhu = models.FloatField(blank=True, null=True)
    updated_by = models.ForeignKey(User, models.DO_NOTHING, db_column='updated_by', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thresholds'

class Upload(models.Model):
    id_upload = models.AutoField(primary_key=True)
    nama_file = models.CharField(max_length=255, blank=True, null=True)
    tanggal_upload = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, db_column='uploaded_by', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'uploads'
