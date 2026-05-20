import time

# Import your notification drivers
from sensors.alerts import update_firebase_cloud, send_emergency_sms
from sensors.kakao_alert import send_kakaotalk_alert

def evaluate_landslide_risk(soil_pct, rain_pct, water_pct, tilt_x):
    """Smart Multi-Vector Risk Assessment Matrix (Unchanged from original)."""
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

# Tracking flags
alert_dispatched = False
current_temp = "23.5"

print("=" * 60)
print("     MOOGUARD CORE ENGINE: HARDWARE SIMULATION MODE       ")
print("=" * 60)
print("Type a number (1-3) to instantly simulate environmental profiles:")
print("1 -> SYSTEM SAFE  (Dry soil, no rain, stable slope)")
print("2 -> CAUTION      (Rising moisture levels, minor warning thresholds)")
print("3 -> EVACUATE     (Critical soil saturation, water pooling, tilt displacement)")
print("-" * 60)

try:
    while True:
        user_choice = input("\nEnter Simulation State Profile Number (1, 2, or 3): ").strip()
        
        # Profile 1: Safe baseline conditions
        if user_choice == "1":
            soil_pct, rain_pct, water_pct, tilt_x = 12.5, 0.0, 5.0, 0.1
        # Profile 2: Warning conditions
        elif user_choice == "2":
            soil_pct, rain_pct, water_pct, tilt_x = 35.0, 20.0, 22.0, 0.9
        # Profile 3: Extreme danger conditions (Triggers all thresholds)
        elif user_choice == "3":
            soil_pct, rain_pct, water_pct, tilt_x = 55.0, 65.0, 48.0, 1.8
        else:
            print("Invalid profile option. Defaulting to safe metrics.")
            soil_pct, rain_pct, water_pct, tilt_x = 12.5, 0.0, 5.0, 0.1

        # Run core risk logic
        system_status = evaluate_landslide_risk(soil_pct, rain_pct, water_pct, tilt_x)
        print(f"\n[SIMULATED TELEMETRY] S:{soil_pct}% | R:{rain_pct}% | W:{water_pct}% | Tilt:{tilt_x}° -> Status: {system_status}")

        # --- CLOUD NOTIFICATION BLOCK ---
        # Sync simulated metrics to Firebase to check your web app updates
        update_firebase_cloud(soil_pct, rain_pct, water_pct, tilt_x, system_status)
        
        # --- CRITICAL ALERT MULTI-CHANNEL DISPATCH ---
        if "EVACUATE" in system_status:
            if not alert_dispatched:
                print("\n🚨 Escalating to emergency notification routing profiles...")
                send_emergency_sms(system_status)
                send_kakaotalk_alert(
                    status_msg=system_status,
                    soil_val=soil_pct,
                    water_val=water_pct,
                    tilt_val=tilt_x
                )
                alert_dispatched = True
        else:
            if alert_dispatched:
                print("\n🟩 Conditions normalized. Resetting communication blocks.")
            alert_dispatched = False

except KeyboardInterrupt:
    print("\nSimulation session terminated cleanly.")