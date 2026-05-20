import board
import adafruit_mpu6050

def get_mpu_sensor():
    """Initializes the I2C MPU6050 sensor."""
    try:
        i2c = board.I2C() 
        mpu = adafruit_mpu6050.MPU6050(i2c)
        return mpu
    except Exception as e:
        print(f"MPU6050 Init Error: {e}")
        return None

def get_tilt_data(mpu):
    """Returns acceleration (X, Y, Z)."""
    if mpu is None:
        return (0.0, 0.0, 9.8) # Mock data if disconnected
    try:
        return mpu.acceleration
    except Exception:
        return (0.0, 0.0, 9.8)