import adafruit_mcp3xxx.analog_in as AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP

def get_rain_sensor_data(mcp, min_v=0.5, max_v=3.3):
    """
    Reads the rain sensor module on CH1 and converts to 0-100% intensity.
    """
    try:
        channel = AnalogIn.AnalogIn(mcp, MCP.P1)
        voltage = channel.voltage
        
        v = max(min_v, min(voltage, max_v))
        percent = 100 - (((v - min_v) / (max_v - min_v)) * 100)
        return round(percent, 1)
    except Exception as e:
        print(f"Rain Sensor Read Error: {e}")
        return 0.0