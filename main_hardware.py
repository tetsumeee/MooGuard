import time
from sensors.mcp_base import get_mcp
from sensors.temp_humidity import get_th_data
from sensors.mpu6050 import get_mpu_sensor, get_tilt_data
from sensors.display_tft import update_tft

# Modular Sensor Drivers
from sensors.soil_moisture import get_soil_moisture_data
from sensors.rain_sensor import get_rain_sensor_data
from sensors.water_level import get_water_level_data

# Alert Notification Drivers
from sensors.alerts import update_supabase_cloud, send_emergency_sms
#from sensors.kakao_alert import send_kakaotalk_alert

# --- CRACK DETECTION ---
from sensors.crack_detector import capture_and_detect, save_evidence, load_references
crack_references = load_references()

# 1. Physical Hardware Initialization
print("Initializing MooGuard Production Hardware Array...")
try:
    mcp = get_mcp()
    mpu = get_mpu_sensor()
    print("MooGuard Core Processing Unit: ONLINE")
except Exception as e:
    print(f"Critical Hardware Boot Failure: {e}")
    exit(1)

def evaluate_landslide_risk(soil_pct, rain_pct, water_pct, tilt_x, crack_severity=None):
    """
    Risk Assessment Matrix.

    EVACUATE (RED):
      - Tilt exceeds critical threshold (>= 1.5°) — slope shift detected
      - OR crack is critical AND tilt is at warning level (>= 0.8°)

    CAUTION (YELLOW):
      - Any sensor threshold exceeded (soil, rain, water, tilt warning, crack warning)
      - Never triggered by tilt alone beyond 1.5° — that goes straight to EVACUATE

    SYSTEM SAFE (GREEN):
      - All readings within normal bounds
    """
    is_tilt_critical  = abs(tilt_x) <= -4.8
    is_tilt_warning   = abs(tilt_x) <= -4
    is_soil_saturated = soil_pct >= 80.0
    is_soil_warning   = soil_pct >= 40.0
    is_heavy_rain     = rain_pct >= 85.0
    is_water_pooling  = water_pct >= 40.0
    is_crack_critical = crack_severity == "critical"
    is_crack_warning  = crack_severity == "warning"

    # --- RED: EVACUATE ---
    if is_tilt_critical:
        return "EVACUATE (SLOPE SHIFT)"
    if is_crack_critical and is_tilt_warning:
        return "EVACUATE (CRACK + TILT)"

    # --- YELLOW: CAUTION ---
    if any([
        is_soil_saturated,
        is_soil_warning,
        is_heavy_rain,
        is_water_pooling,
        is_tilt_warning,
        is_crack_warning,
    ]):
        return "CAUTION"

    return "SYSTEM SAFE"

# 2. Operational Telemetry Timelines
SENSOR_INTERVAL        = 10.0
CRACK_INTERVAL_NORMAL  = 300.0   # 5 minutes during normal operation
CRACK_INTERVAL_ALERT   = 10.0    # 10 seconds during warning/evacuate

last_sensor_read   = 0.0
last_crack_capture = 0.0
current_temp       = "--"
current_crack_severity = None

# Communication Safety Flags
alert_dispatched = False

try:
    while True:
        current_time = time.time()

        # --- SENSOR POLLING CYCLE ---
        if current_time - last_sensor_read >= SENSOR_INTERVAL:
            soil_pct  = get_soil_moisture_data(mcp)
            rain_pct  = get_rain_sensor_data(mcp)
            water_pct = get_water_level_data(mcp)

            accel  = get_tilt_data()
            tilt_x = round(accel[0], 1)

            t, _ = get_th_data()
            if t is not None:
                current_temp = f"{round(t, 1)}"

            system_status = evaluate_landslide_risk(
                soil_pct, rain_pct, water_pct, tilt_x, current_crack_severity
            )

            update_tft(rain_pct, soil_pct, water_pct, current_temp, tilt_x, system_status)
            update_supabase_cloud(soil_pct, rain_pct, water_pct, tilt_x, system_status)

            # --- EMERGENCY DUAL-CHANNEL TELECOMMUNICATIONS ---
            if "EVACUATE" in system_status:
                if not alert_dispatched:
                    send_emergency_sms(system_status)
                    #send_kakaotalk_alert(system_status, soil_pct, water_pct, tilt_x)
                    alert_dispatched = True
            else:
                alert_dispatched = False

            print(f"[LIVE HARDWARE] S:{soil_pct}% | R:{rain_pct}% | W:{water_pct}% | Tilt:{tilt_x}° | Crack:{current_crack_severity} -> {system_status}")
            last_sensor_read = current_time

        # --- CRACK DETECTION CYCLE ---
        # Use fast interval if system is in alert state, otherwise slow interval
        is_alert_active = "EVACUATE" in (
            evaluate_landslide_risk(0, 0, 0, 0, current_crack_severity)  # tilt/crack only check
        ) or current_crack_severity in ("warning", "critical")

        crack_interval = CRACK_INTERVAL_ALERT if is_alert_active else CRACK_INTERVAL_NORMAL

        if current_time - last_crack_capture >= crack_interval:
            try:
                result = capture_and_detect(references=crack_references)

                if result:
                    current_crack_severity = result["severity"]
                    print(f"[CRACK DETECT] Coverage:{result['crack_area_pct']}% | Severity:{current_crack_severity}")

                    save_evidence(result)

                    from sensors.alerts import update_supabase_crack
                    update_supabase_crack(result['crack_count'], result['crack_area_pct'], current_crack_severity)
                else:
                    print("[CRACK DETECT] ⚠️ No result from capture_and_detect()")

                last_crack_capture = current_time
            except Exception as e:
                print(f"[CRACK DETECT] ❌ Error: {e}")
                last_crack_capture = current_time  # Prevent tight retry loop on error

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nHardware execution paused cleanly by operator.")
