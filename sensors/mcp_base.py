import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP

def get_mcp():
    """Initializes and returns the MCP3008 ADC object on SPI."""
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D8)  # CE0 (GPIO 8)
    mcp = MCP.MCP3008(spi, cs)
    return mcp