import time
import board
import adafruit_dht

# Set use_pulseio=False to bypass the libgpiod requirement
dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

def get_th_data():
    try:
        temp = dht_device.temperature
        hum = dht_device.humidity
        return temp, hum
    except RuntimeError as e:
        # These errors are normal for DHT sensors; they just mean a missed pulse
        return None, None

if __name__ == "__main__":
    print("Testing DHT22 without PulseIO...")
    while True:
        t, h = get_th_data()
        if t is not None:
            print(f"Temp: {t:.1f}C | Humidity: {h:.1f}%")
        else:
            print("Retrying...")
        time.sleep(2.0)