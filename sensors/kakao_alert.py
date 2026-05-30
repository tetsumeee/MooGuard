"""
MooGuard Kakao Talk Notifications
Three implementation options below - uncomment the one you use
"""

import requests
import json

# ============================================================================
# OPTION 1: Kakao Talk Messaging API (requires business account + API key)
# https://developers.kakao.com/docs/latest/ko/message/common
# ============================================================================

def send_kakaotalk_alert_option1(status, soil_pct, water_pct, tilt_x):
    """Send alert via Kakao Talk Messaging API"""
    
    KAKAO_API_KEY = "f0de8b12c68240b1d10a3de5e1d1edde"  # Get from Kakao Developers
    KAKAO_USER_ID = "frw1lVa590VAibfZxsS-FWF0nHwVSI2JAAAAAQoXEC8AAAGeeg6W2f8D-j8FVvr5"        # Your Kakao Talk User ID
    
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    headers = {
        "Authorization": f"Bearer {KAKAO_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    message = f"""
⚠️ [MooGuard 위급 경보]
산사태 위험이 감지되었습니다!

상태: {status}
토양습도: {soil_pct}%
수위: {water_pct}%
경사도: {tilt_x}°

즉시 대피하십시오!
    """.strip()
    
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://your-mooguard-dashboard.com",
                "mobile_web_url": "https://your-mooguard-dashboard.com"
            }
        })
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("[KAKAO] ✅ Alert sent to Kakao Talk")
        else:
            print(f"[KAKAO] ❌ Failed: {response.text}")
    except Exception as e:
        print(f"[KAKAO] ❌ Error: {e}")


# ============================================================================
# OPTION 2: Kakao Work (if using enterprise Kakao)
# ============================================================================

def send_kakaotalk_alert_option2(status, soil_pct, water_pct, tilt_x):
    """Send alert via Kakao Work (enterprise messaging)"""
    
    KAKAO_WORK_BOT_ID = "YOUR_BOT_ID"
    KAKAO_WORK_SPACE_ID = "YOUR_SPACE_ID"
    KAKAO_WORK_API_KEY = "YOUR_KAKAO_WORK_API_KEY"
    
    url = f"https://api.kakaowork.com/v1/messages"
    
    headers = {
        "Authorization": f"Bearer {KAKAO_WORK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    message_text = f"""
🚨 MooGuard 긴급 경보
상태: {status}
토양습도: {soil_pct}% | 수위: {water_pct}% | 경사도: {tilt_x}°
⚠️ 즉시 대피하십시오!
    """.strip()
    
    payload = {
        "text": message_text,
        "channel_id": KAKAO_WORK_SPACE_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("[KAKAO WORK] ✅ Alert sent")
        else:
            print(f"[KAKAO WORK] ❌ Failed: {response.text}")
    except Exception as e:
        print(f"[KAKAO WORK] ❌ Error: {e}")


# ============================================================================
# OPTION 3: Kakao iOG (Open Graph) + Custom Bot
# ============================================================================

def send_kakaotalk_alert_option3(status, soil_pct, water_pct, tilt_x):
    """Send via Kakao i Open Builder (chatbot)"""
    
    KAKAO_BOT_API_URL = "YOUR_BOT_API_ENDPOINT"  # Your custom bot webhook
    
    payload = {
        "text": f"⚠️ [{status}] 산사태 위험 감지",
        "details": {
            "soil_moisture": soil_pct,
            "water_level": water_pct,
            "tilt": tilt_x,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        },
        "alert_level": "critical" if "EVACUATE" in status else "warning"
    }
    
    try:
        response = requests.post(KAKAO_BOT_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print("[KAKAO BOT] ✅ Alert sent")
        else:
            print(f"[KAKAO BOT] ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"[KAKAO BOT] ❌ Error: {e}")


# ============================================================================
# MAIN FUNCTION (use this in main_hardware.py)
# ============================================================================

def send_kakaotalk_alert(status, soil_pct, water_pct, tilt_x):
    """
    Main alert function - calls the implementation you choose.
    Edit this to uncomment your chosen option.
    """
    
    # Choose ONE of these three:
    
    # Option 1: Kakao Talk Messaging API (recommended for individual users)
    send_kakaotalk_alert_option1(status, soil_pct, water_pct, tilt_x)
    
    # Option 2: Kakao Work (enterprise)
    # send_kakaotalk_alert_option2(status, soil_pct, water_pct, tilt_x)
    
    # Option 3: Custom Bot
    # send_kakaotalk_alert_option3(status, soil_pct, water_pct, tilt_x)


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
OPTION 1: Kakao Talk Messaging API (Easiest for students)
─────────────────────────────────────────────────────────

1. Go to: https://developers.kakao.com/
2. Sign in with Kakao account
3. Create new app → choose "Web"
4. Go to "앱 설정" → "앱 키" → Copy "REST API 키"
5. Enable "Kakao Talk Message" product
6. Go to "Kakao Talk Message" → Enable sending to yourself
7. Get your Kakao Talk User ID:
   - Open https://developers.kakao.com/tool/rest-api/open/get/v2-user-me
   - Click "실행" (Run) → see your user ID in response
8. Replace YOUR_KAKAO_REST_API_KEY and YOUR_KAKAO_USER_ID above

OPTION 2: Kakao Work (Enterprise)
──────────────────────────────────
Ask Prof. Victoria Kim or Prof. Mehdi if your school has Kakao Work.

OPTION 3: Custom Kakao i Bot
─────────────────────────────
1. Create bot on https://i.kakao.com/
2. Set webhook URL in this file
3. Bot receives alerts via HTTP POST

TEST IT:
────────
python3 << 'EOF'
from sensors.kakao_alert import send_kakaotalk_alert
send_kakaotalk_alert("EVACUATE (TEST)", 45, 35, 1.2)
EOF
"""
