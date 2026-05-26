import time
from supabase import create_client, Client
from twilio.rest import Client as TwilioClient

# --- 1. SUPABASE CONFIGURATION ---
# Paste your Supabase Project URL and anon public key here
SUPABASE_URL = "https://ubzozdnrkznhsgwhcmlu.supabase.co"
SUPABASE_KEY = "sb_publishable_AATjrsTM0FLz35ILJEA_-A_Z3rdTEx9"

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. TWILIO CONFIGURATION ---
TWILIO_ACCOUNT_SID = "AC1c64dc8a4ccae8be267418f0e41c5186"
TWILIO_AUTH_TOKEN  = "28d6e4b2a82ae51ac0b8607821705311"
TWILIO_NUMBER      = "+13613016253" 
MY_PHONE_NUMBER    = "+821057272266" 

def update_supabase_cloud(soil_pct, rain_pct, water_pct, tilt_x, status):
    """Pushes real-time simulation metrics up to your Supabase PostgreSQL database."""
    try:
        # The keys here must exactly match the column names in your SQL table
        data, count = supabase.table('telemetry_logs').insert({
            "soil_moisture": soil_pct,
            "precipitation": rain_pct,
            "water_level": water_pct,
            "ground_tilt": tilt_x,
            "risk_status": status
        }).execute()
        
        print("[CLOUD SYNC] ✅ Telemetry pushed to Supabase Database.")
    except Exception as e:
        print(f"[CLOUD SYNC] ❌ Supabase sync failed: {e}")

def send_emergency_sms(status):
    """Dispatches a critical text message alert directly to your phone."""
    if "your_auth_token" in TWILIO_AUTH_TOKEN:
        print("[SMS DISPATCH] ⚠️ Twilio credentials are placeholders. Skipping SMS.")
        return

    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"⚠️ [MooGuard 위급 경보] 산사태 위험이 감지되었습니다! 현재 시스템 상태: {status}. 즉시 대피하십시오!",
            from_=TWILIO_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(f"[SMS DISPATCH] 📱 Emergency text sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"[SMS DISPATCH] ❌ Twilio transmission failed: {e}")
