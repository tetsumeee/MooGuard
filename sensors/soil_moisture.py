import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# 1. Hardware Setup (The SPI connection we fixed)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)

# 2. Assign the Soil Sensor to Channel 0
soil_channel = AnalogIn(mcp, MCP.P0)

# 3. Calibration Thresholds (Adjust these based on your tests)
# Most sensors: 3.3V = Dry, 0.5V = Very Wet
WET_LIMIT = 1.2  # Below this = Saturated
DRY_LIMIT = 2.5  # Above this = Dry

print("--- MooGuard: Soil Sensor Standalone Test ---")
print("Press Ctrl+C to stop the script.")

try:
    while True:
        # Get the current voltage from the sensor
        voltage = soil_channel.voltage
        
        # Determine the status
        if voltage < WET_LIMIT:
            status = "SATURATED (High Landslide Risk)"
        elif voltage < DRY_LIMIT:
            status = "DAMP (Monitor closely)"
        else:
            status = "DRY (Safe)"
            
        # Calculate a rough percentage (0% to 100%)
        # Inverting the math because lower voltage means more water
        moisture_percent = (1 - (voltage / 3.3)) * 100
        moisture_percent = max(0, min(100, moisture_percent)) # Keep between 0-100

        # Print the results
        print(f"Voltage: {round(voltage, 2)}V | Moisture: {round(moisture_percent, 1)}% | Status: {status}")
        
        time.sleep(15)

except KeyboardInterrupt:
    print("\nTest stopped by user.")