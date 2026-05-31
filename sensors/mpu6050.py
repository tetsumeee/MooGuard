import board
import adafruit_mpu6050
import time

# Module-level sensor instance (safe initialization)
_mpu = None

def get_mpu_sensor():
    """Initializes the I2C MPU6050 sensor."""
    global _mpu
    try:
        i2c = board.I2C()
        _mpu = adafruit_mpu6050.MPU6050(i2c)
        print("[MPU6050] ✅ Sensor initialized")
        return _mpu
    except Exception as e:
        print(f"[MPU6050] ⚠️ Not connected: {e}")
        return None

def get_tilt_data():
    """Returns acceleration (X, Y, Z). Returns mock data if disconnected."""
    if _mpu is None:
        return (0.0, 0.0, 9.8)
    try:
        return _mpu.acceleration
    except Exception:
        return (0.0, 0.0, 9.8)

if __name__ == "__main__":
    print("Testing MPU6050 Tilt Sensor...")
    sensor = get_mpu_sensor()
    while True:
        accel = get_tilt_data()
        print(f"Accel: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
        time.sleep(1)
