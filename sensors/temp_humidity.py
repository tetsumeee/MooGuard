import board
import adafruit_dht

# DHT22 connected to GPIO 4 (Pin 7)
dht_device = adafruit_dht.DHT22(board.D4)

def get_th_data():
    """Reads temperature and humidity. Returns (Temp, Hum) or (None, None) on error."""
    try:
        temp = dht_device.temperature
        hum = dht_device.humidity
        return temp, hum
    except RuntimeError:
        # DHT sensors frequently throw read errors, which is normal.
        return None, None