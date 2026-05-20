import adafruit_mcp3xxx.analog_in as AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP

def get_water_level_data(mcp, min_v=0.0, max_v=2.5):
    """
    Reads the standing water level sensor on CH3 and converts to 0-100% depth.
    """
    try:
        channel = AnalogIn.AnalogIn(mcp, MCP.P3)
        voltage = channel.voltage
        
        v = max(min_v, min(voltage, max_v))
        # Direct percentage conversion because higher voltage means more water pooling
        percent = ((v - min_v) / (max_v - min_v)) * 100
        return round(percent, 1)
    except Exception as e:
        print(f"Water Level Read Error: {e}")
        return 0.0