import time
import board
import adafruit_mpu6050

# Initialize I2C and MPU6050
i2c = board.I2C() 
mpu = adafruit_mpu6050.MPU6050(i2c)

def get_tilt_data():
    """
    Returns acceleration (m/s^2) and gyro (degrees/s) data.
    """
    # Returns (x, y, z) tuples
    return mpu.acceleration, mpu.gyro

if __name__ == "__main__":
    print("Testing MPU6050 Tilt Sensor...")
    while True:
        accel, gyro = get_tilt_data()
        print(f"Accel: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
        print(f"Gyro: X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
        time.sleep(1)
