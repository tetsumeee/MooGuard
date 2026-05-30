import requests
import json
from datetime import datetime

# ============================================================================
# OPTION 1: Kakao Talk Messaging API (send to myself)
# https://developers.kakao.com/docs/latest/ko/message/common
# ============================================================================

def send_kakaotalk_alert(status, soil_pct, water_pct, tilt_x):
    """Send alert via Kakao Talk Messaging API to yourself"""
    
    KAKAO_API_KEY = "frw1lVa590VAibfZxsS-FWF0nHwVSI2JAAAAAQoXEC8AAAGeeg6W2f8D-j8FVvr5"  # Get from App Settings > App Keys
    
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

시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

즉시 대피하십시오!
    """.strip()
    
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://mooguard.local",
            }
        })
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("[KAKAO] ✅ Alert sent to Kakao Talk")
            return True
        else:
            print(f"[KAKAO] ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[KAKAO] ❌ Error: {e}")
        return False
