import serial
import json
import time
import csv
import os
import paho.mqtt.client as mqtt
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

# --- SERIAL SETTINGS ---
# Windows: 'COM3' etc. | Linux/Mac: '/dev/ttyUSB0'
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

# --- DATA STORAGE SETTINGS ---
# Get directory of this script to create 'data' folder relatively
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- MQTT SETTINGS (Select ONE option) ---

# OPTION 1: Public Mosquitto (Testing)
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "bioeconomy/textile_bin/1"
ACCESS_TOKEN = None 

# OPTION 2: ThingsBoard (Production)
# MQTT_BROKER = "demo.thingsboard.io"
# MQTT_PORT = 1883
# MQTT_TOPIC = "v1/devices/me/telemetry"
# ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_current_csv_path():
    """
    Returns the path for the current month's CSV file.
    Example: .../edge_gateway/data/sensor_data_2023-11.csv
    """
    current_month = datetime.now().strftime('%Y-%m')
    filename = f"sensor_data_{current_month}.csv"
    return os.path.join(DATA_DIR, filename)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connected to Broker: {MQTT_BROKER}")
    else:
        print(f"[MQTT] Connection Failed. Return code: {rc}")

# ==========================================
# MAIN PROGRAM
# ==========================================

client = mqtt.Client()
if ACCESS_TOKEN:
    client.username_pw_set(ACCESS_TOKEN)
client.on_connect = on_connect

try:
    print(f"[MQTT] Connecting to {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"[MQTT] Error: {e}")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[SERIAL] Listening on {SERIAL_PORT}...")
    print(f"[DATA] Saving data to folder: {DATA_DIR}")
    
    while True:
        if ser.in_waiting > 0:
            try:
                # 1. Read & Parse
                line = ser.readline().decode('utf-8').strip()
                data = json.loads(line)
                
                # Add Timestamp
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                data['timestamp'] = current_time
                
                print(f"Received: {data}")
                
                # 2. Publish to Cloud
                client.publish(MQTT_TOPIC, json.dumps(data))
                
                # 3. Save to Local Storage (Monthly Rotation)
                csv_path = get_current_csv_path()
                file_exists = os.path.isfile(csv_path)
                
                with open(csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # Write headers only if file is new
                    if not file_exists:
                        writer.writerow(["timestamp", "distance_cm", "temperature_c", "humidity_pct"])
                        print(f"[DATA] Created new log file: {csv_path}")
                    
                    writer.writerow([
                        data['timestamp'], 
                        data.get('distance_cm'), 
                        data.get('temperature_c'), 
                        data.get('humidity_pct')
                    ])
                
            except json.JSONDecodeError:
                pass # Ignore partial lines
            except Exception as e:
                print(f"[ERROR] {e}")
                
except KeyboardInterrupt:
    print("\n[SYSTEM] Stopping gateway...")
    client.loop_stop()
    if 'ser' in locals() and ser.is_open:
        ser.close()