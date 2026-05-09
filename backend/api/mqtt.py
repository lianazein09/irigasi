import paho.mqtt.client as mqtt
import json
from django.conf import settings
from .models import TelemetryLog, SprinklerLog, Sensor

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"Connected to MQTT Broker: {settings.MQTT_BROKER_HOST}")
        client.subscribe("tani_cerdas/telemetry")
        client.subscribe("tani_cerdas/sprinkler/log")
    else:
        print(f"Failed to connect to MQTT Broker, return code {reason_code}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"Received message on {topic}: {payload}")
        
        if topic == "tani_cerdas/telemetry":
            # Expected payload: {"id_sensor": 1, "nilai_sensor": 45.5}
            id_sensor_val = payload.get("id_sensor")
            nilai = payload.get("nilai_sensor")
            
            if id_sensor_val and nilai is not None:
                try:
                    sensor = Sensor.objects.get(id_sensor=id_sensor_val)
                    # Use auto_now_add logic or pass timezone.now() if needed.
                    # Based on models.py, timestamp in TelemetryLog doesn't have auto_now_add
                    from django.utils import timezone
                    TelemetryLog.objects.create(
                        id_sensor=sensor,
                        nilai_sensor=nilai,
                        timestamp=timezone.now()
                    )
                    print("Telemetry saved.")
                except Sensor.DoesNotExist:
                    print(f"Sensor with id {id_sensor_val} does not exist.")
                    
        elif topic == "tani_cerdas/sprinkler/log":
            # Expected payload: {"status": "ON", "sumber": "otomatis"}
            status = payload.get("status")
            sumber = payload.get("sumber")
            
            if status in ["ON", "OFF"] and sumber in ["manual", "otomatis"]:
                from django.utils import timezone
                SprinklerLog.objects.create(
                    status=status,
                    sumber=sumber,
                    waktu=timezone.now()
                )
                print("Sprinkler log saved.")
                
    except json.JSONDecodeError:
        print(f"Error decoding JSON payload from topic {msg.topic}: {msg.payload}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# Initialize client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

def start_mqtt_client():
    print("Initializing MQTT Client...")
    try:
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        client.loop_start()
        print("MQTT Client loop started successfully.")
    except Exception as e:
        print(f"Failed to start MQTT client: {e}")

def publish_message(topic, message):
    try:
        client.publish(topic, json.dumps(message))
        return True
    except Exception as e:
        print(f"Failed to publish message: {e}")
        return False
