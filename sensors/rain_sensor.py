import time
from mcp_base import get_mcp
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

mcp = get_mcp()
rain_channel = AnalogIn(mcp, MCP.P1)

# Thresholds: Dry is usually ~3.3V, Heavy Rain < 1.0V
def get_rain_data():
    v = round(rain_channel.voltage, 2)
    if v > 3.0:
        status = "Dry"
    elif v > 1.5:
        status = "Light Rain"
    else:
        status = "Heavy Rain"
    return v, status

if __name__ == "__main__":
    try:
        while True:
            volts, msg = get_rain_data()
            print(f"Rain Voltage: {volts}V | Status: {msg}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass