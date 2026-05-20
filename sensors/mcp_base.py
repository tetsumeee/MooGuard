import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP

def get_mcp():
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D8)
    return MCP.MCP3008(spi, cs)