import adafruit_mcp3xxx.analog_in as AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP

def get_soil_moisture_data(mcp, min_v=0.5, max_v=3.3):
    """
    Reads the capacitive soil moisture sensor on CH0 and converts to 0-100%.
    Standard calibration: Typical analog soil probes drop voltage as moisture increases.
    """
    try:
        channel = AnalogIn.AnalogIn(mcp, MCP.P0)
        voltage = channel.voltage
        
        # Clamp voltage to safe calibration limits
        v = max(min_v, min(voltage, max_v))
        # Invert percentage calculation because lower voltage means higher moisture
        percent = 100 - (((v - min_v) / (max_v - min_v)) * 100)
        return round(percent, 1)
    except Exception as e:
        print(f"Soil Moisture Read Error: {e}")
        return 0.0