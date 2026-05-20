import time
from mcp_base import get_mcp
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

mcp = get_mcp()
water_channel = AnalogIn(mcp, MCP.P3)

def get_water_data():
    """
    Returns raw voltage.
    Dry/Empty: ~0.0V
    Fully Submerged: Up to ~2.5V - 3.0V (Depends on water purity)
    """
    v = round(water_channel.voltage, 2)
    
    # Simple threshold categorization
    if v < 0.5:
        status = "Empty/Dry"
    elif v < 1.5:
        status = "Low Level"
    elif v < 2.3:
        status = "Medium Level"
    else:
        status = "High/Flood Risk"
        
    return v, status

if __name__ == "__main__":
    print("Testing Water Level Sensor... Dip it into a cup of water step-by-step.")
    try:
        while True:
            volts, level = get_water_data()
            print(f"Water Voltage: {volts}V | Level: {level}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass