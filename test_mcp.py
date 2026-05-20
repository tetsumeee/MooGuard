import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Initialize SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
mcp = MCP.MCP3008(spi, cs)

# Create an input on Channel 0
channel = AnalogIn(mcp, MCP.P0)

print("Starting MCP3008 Test... Press Ctrl+C to stop.")
try:
    while True:
        print(f"Voltage: {round(channel.voltage, 2)}V | Raw Value: {channel.value}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Test stopped.")


