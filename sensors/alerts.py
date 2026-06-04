import requests
from supabase import create_client, Client

# --- 1. SUPABASE CONFIGURATION ---
SUPABASE_URL = "https://ubzozdnrkznhsgwhcmlu.supabase.co"
SUPABASE_KEY = "sb_publishable_AATjrsTM0FLz35ILJEA_-A_Z3rdTEx9"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. MYSMSGATE CONFIGURATION ---
API_KEY         = "4ccb914a-98a6-4f56-b979-c9fec78e1762"
DEVICE_ID       = "22843ad2-8057-4d77-93ba-b0c946450bd9"
API_URL         = "https://mysmsgate.net/api/v1/send"
MY_PHONE_NUMBER = "+821057272266"


def update_supabase_cloud(soil_pct, rain_pct, water_pct, tilt_x, status):
    """Pushes real-time simulation metrics up to your Supabase PostgreSQL database."""
    try:
        supabase.table('telemetry_logs').insert({
            "soil_moisture": soil_pct,
            "precipitation": rain_pct,
            "water_level": water_pct,
            "ground_tilt": tilt_x,
            "risk_status": status
        }).execute()
        print("[CLOUD SYNC] ✅ Telemetry pushed to Supabase Database.")
    except Exception as e:
        print(f"[CLOUD SYNC] ❌ Supabase sync failed: {e}")


def update_supabase_crack(crack_count, crack_area_pct, severity):
    """Updates the latest telemetry row with crack detection results."""
    try:
        latest = supabase.table('telemetry_logs')\
            .select('id')\
            .eq('sensor_type', 'sensor')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        if latest.data:
            row_id = latest.data[0]['id']
            supabase.table('telemetry_logs').update({
                "crack_count":    crack_count,
                "crack_area_pct": crack_area_pct,
            }).eq('id', row_id).execute()
            print(f"[CRACK SYNC] ✅ Crack data updated — severity: {severity}")
        else:
            print("[CRACK SYNC] ⚠️ No sensor rows found to update")
    except Exception as e:
        print(f"[CRACK SYNC] ❌ Crack sync failed: {e}")


def send_emergency_sms(status):
    """Dispatches a critical text message alert via MySMSGate."""
    payload = {
        "to":      MY_PHONE_NUMBER,
        "message": f"⚠️ [MooGuard 위급 경보] 산사태 위험이 감지되었습니다! 현재 시스템 상태: {status}. 즉시 대피하십시오!",
        "device":  DEVICE_ID
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json"
    }
    try:
        print(f"[SMS DISPATCH] Sending alert to {MY_PHONE_NUMBER}...")
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print("[SMS DISPATCH] 📱 Emergency text sent successfully!")
        else:
            print(f"[SMS DISPATCH] ❌ Failed — HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[SMS DISPATCH] ❌ Network error: {e}")
