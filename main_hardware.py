import time
from sensors.mcp_base import get_mcp
from sensors.temp_humidity import get_th_data
from sensors.mpu6050 import get_mpu_sensor, get_tilt_data
from sensors.display_tft import update_tft

# Modular Sensor Drivers
from sensors.soil_moisture import get_soil_moisture_data
from sensors.rain_sensor import get_rain_sensor_data
from sensors.water_level import get_water_level_data
from sensors.camera_control import MooGuardCamera

# Alert Notification Drivers
from sensors.alerts import update_firebase_cloud, send_emergency_sms
from sensors.kakao_alert import send_kakaotalk_alert

# 1. Physical Hardware Initialization
print("Initializing MooGuard Production Hardware Array...")
try:
    mcp = get_mcp()
    mpu = get_mpu_sensor()
    camera = MooGuardCamera()
    print("MooGuard Core Processing Unit: ONLINE [cite: 109]")
except Exception as e:
    print(f"Critical Hardware Boot Failure: {e}")
    exit(1)

def evaluate_landslide_risk(soil_pct, rain_pct, water_pct, tilt_x):
    """Smart Multi-Vector Risk Assessment Matrix."""
    is_soil_saturated = soil_pct >= 45.0
    is_soil_warning   = soil_pct >= 30.0
    is_heavy_rain     = rain_pct >= 45.0
    is_water_pooling  = water_pct >= 40.0
    is_tilt_critical  = abs(tilt_x) >= 1.5
    is_tilt_warning   = abs(tilt_x) >= 0.8
    
    if is_tilt_critical:
        return "EVACUATE (SLOPE SHIFT)"
    elif is_soil_saturated and (is_heavy_rain or is_water_pooling):
        return "EVACUATE (MUDSLIDE)"
    elif is_soil_warning or is_tilt_warning or is_water_pooling:
        return "CAUTION"
    return "SYSTEM SAFE"

# 2. Operational Telemetry Timelines (10-Second Intervals)
SENSOR_INTERVAL = 10.0   
last_sensor_read = 0.0
last_camera_capture = 0.0
current_temp = "--"

# Communication Safety Flags
alert_dispatched = False

try:
    while True:
        current_time = time.time()
        
        # --- HARDWARE POLLING CYCLE ---
        if current_time - last_sensor_read >= SENSOR_INTERVAL:
            # Gather real-time data from physical hardware layers
            soil_pct = get_soil_moisture_data(mcp)
            rain_pct = get_rain_sensor_data(mcp)
            water_pct = get_water_level_data(mcp)

            accel = get_tilt_data(mpu)
            tilt_x = round(accel[0], 1)
            
            t, _ = get_th_data()
            if t is not None:
                current_temp = f"{round(t, 1)}"
                
            # Process safety risk calculations
            system_status = evaluate_landslide_risk(soil_pct, rain_pct, water_pct, tilt_x)

            # Redraw local landscape TFT dashboard graphics
            update_tft(rain_pct, soil_pct, water_pct, current_temp, tilt_x, system_status)
            
            # Replicate live metrics to cloud web dashboard
            update_firebase_cloud(soil_pct, rain_pct, water_pct, tilt_x, system_status)
            
            # --- EMERGENCY DUAL-CHANNEL TELECOMMUNICATIONS ---
            if "EVACUATE" in system_status:
                if not alert_dispatched:
                    send_emergency_sms(system_status) [cite: 305]
                    send_kakaotalk_alert(system_status, soil_pct, water_pct, tilt_x) [cite: 305]
                    alert_dispatched = True
            else:
                alert_dispatched = False

            print(f"[LIVE HARDWARE] S:{soil_pct}% | R:{rain_pct}% | W:{water_pct}% | Tilt:{tilt_x}° -> {system_status}")
            last_sensor_read = current_time

        # --- ADAPTIVE SURVEILLANCE TIMELINE ---
        camera_interval = 10.0 if ("EVACUATE" in system_status or "CAUTION" in system_status) else 300.0

        if current_time - last_camera_capture >= camera_interval:
            camera.capture_evidence_frame(status=system_status.split(" ")[0])
            last_camera_capture = current_time

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nHardware execution paused cleanly by operator.")
    camera.close()