import time
import adafruit_mcp3xxx.analog_in as AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP

from sensors.mcp_base import get_mcp
from sensors.temp_humidity import get_th_data
from sensors.display_tft import update_tft

# 1. System Hardware Engine Startup
try:
    mcp = get_mcp()
    soil_channel = AnalogIn.AnalogIn(mcp, MCP.P0)   # CH0
    rain_channel = AnalogIn.AnalogIn(mcp, MCP.P1)   # CH1
    water_channel = AnalogIn.AnalogIn(mcp, MCP.P3)  # CH3
    print("MooGuard Core Processing Unit: ONLINE")
except Exception as e:
    print(f"Critical Hardware Initialization Failure: {e}")
    exit(1)

# 2. Future MPU6050 Hardware Placeholder Block
# Set this to False when your physical MPU6050 module arrives
USE_MOCK_GYRO = True 

if not USE_MOCK_GYRO:
    try:
        from sensors.tilt_sensor import get_tilt_data
        print("Hardware Inclinometer Connection Linked.")
    except ImportError:
        print("Warning: tilt_sensor.py missing. Defaulting to Mock tracking.")
        USE_MOCK_GYRO = True

def read_gyroscope():
    """Reads real tilt telemetry or executes mock state tracking if detached."""
    if USE_MOCK_GYRO:
        # Emulates nominal gravitational Z-force equilibrium stability
        return "X:0.00 Y:0.00"
    try:
        accel, gyro = get_tilt_data()
        return f"X:{accel[0]:.1f} Y:{accel[1]:.1f}"
    except Exception:
        return "ERROR"

def evaluate_landslide_risk(soil_v, rain_v, water_v, gyro_str):
    """Applies strict conditional matrices to evaluate structural safety zones."""
    # Flag criteria
    is_saturated = soil_v < 1.2 and rain_v < 1.0
    is_flooding = water_v > 2.3
    
    # Simple alert logic if structural displacement is registered via real gyro
    has_shifted = False
    if "X:" in gyro_str and not USE_MOCK_GYRO:
        try:
            # Parses numerical vector shifts from the interface data stream
            x_val = abs(float(gyro_str.split("X:")[1].split(" ")[0]))
            if x_val > 3.0: # Arbitrary baseline angle threshold tilt validation
                has_shifted = True
        except ValueError:
            pass

    if is_saturated or is_flooding or has_shifted:
        return "EVACUATE"
    elif soil_v < 1.8 or rain_v < 1.8 or water_v > 1.0:
        return "CAUTION"
    return "SYSTEM SAFE"

# 3. Execution Tracking Invariants
last_dht_read = 0
current_temp = "--"

print("Beginning active data loop telemetry tracking...")

try:
    while True:
        # Harvest Analog data streams
        soil_v = round(soil_channel.voltage, 2)
        rain_v = round(rain_channel.voltage, 2)
        water_v = round(water_channel.voltage, 2)

        # Handle throttled asynchronous execution timing for DHT22
        if time.time() - last_dht_read > 3.0:
            t, _ = get_th_data()
            if t is not None:
                current_temp = f"{round(t, 1)}"
            last_dht_read = time.time()

        # Handle Inclinometer/Gyro readings
        gyro_data = read_gyroscope()

        # Evaluate current security thresholds
        system_status = evaluate_landslide_risk(soil_v, rain_v, water_v, gyro_data)

        # Push compiled frames directly to the landscape TFT panel
        update_tft(
            rain=f"{rain_v:.2f}", 
            soil=f"{soil_v:.2f}", 
            water=f"{water_v:.2f}", 
            temp=current_temp, 
            gyro=gyro_data, 
            status=system_status
        )
        
        # Consistent console logs mirroring for configuration debugging tasks
        print(f"[SYSTEM MATRIX] S:{soil_v}V | R:{rain_v}V | W:{water_v}V | T:{current_temp}C | G:[{gyro_data}] -> {system_status}")
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nExecution terminated cleanly by operator interface command.")


