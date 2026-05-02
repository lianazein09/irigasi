from rest_framework import serializers
from .models import Device, Sensor, TelemetryLog, SprinklerLog, DailyReport

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

class TelemetryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryLog
        fields = '__all__'

class SprinklerLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SprinklerLog
        fields = '__all__'

class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = '__all__'
