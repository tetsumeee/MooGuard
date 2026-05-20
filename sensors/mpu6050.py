import time
import board
import adafruit_mpu6050

# Initialize I2C
i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)

def get_tilt_data():
    """Returns Acceleration (m/s^2) and Gyro (degrees/s)"""
    accel = mpu.acceleration
    gyro = mpu.gyro
    return accel, gyro

if __name__ == "__main__":
    print("MPU6050 Test... Tilt the sensor to see changes.")
    try:
        while True:
            a, g = get_tilt_data()
            print(f"Accel X:{a[0]:.2f}, Y:{a[1]:.2f}, Z:{a[2]:.2f} m/s^2")
            # If Z is ~9.8, it is flat. If X or Y move, it is tilting.
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass