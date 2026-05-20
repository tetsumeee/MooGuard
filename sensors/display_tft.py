import os
import board
import busio
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import ili9341

# Pin Connections
cs_pin = digitalio.DigitalInOut(board.D7)  # CE1 (GPIO 7)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
disp = ili9341.ILI9341(spi, rotation=90, cs=cs_pin, dc=dc_pin, rst=reset_pin)

width, height = 320, 240
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

def draw_logo():
    if os.path.exists("logo.png"):
        try:
            logo = Image.open("logo.png").convert("RGB").resize((30, 30))
            image.paste(logo, (10, 5))
            return
        except Exception:
            pass
    draw.polygon([(25, 5), (40, 12), (40, 25), (25, 35), (10, 25), (10, 12)], fill=(0, 150, 255))

def update_tft(rain_pct, soil_pct, water_pct, temp, tilt_x, status):
    draw.rectangle((0, 0, width, height), fill=(10, 16, 26))
    draw.rectangle((0, 0, width, 40), fill=(21, 29, 43))
    draw_logo()
    draw.text((50, 15), "MOOGUARD CORE MONITOR", fill=(255, 255, 255))
    
    if "EVACUATE" in status:
        status_bg, text_color = (180, 0, 0), (255, 255, 255)
    elif "CAUTION" in status:
        status_bg, text_color = (230, 140, 0), (255, 255, 255)
    else:
        status_bg, text_color = (20, 80, 40), (200, 255, 200)
        
    draw.rectangle((210, 8, 310, 32), fill=status_bg, outline=(255,255,255), width=1)
    draw.text((220, 14), status, fill=text_color)

    start_y = 50
    row_h = 34
    spacing = 4
    
    metrics = [
        ("Precipitation (Rain)", f"{rain_pct}%", (0, 210, 255)),
        ("Ground Saturation", f"{soil_pct}%", (50, 255, 100)),
        ("Accumulated Runoff", f"{water_pct}%", (173, 216, 230)),
        ("Ambient Core Temp", f"{temp} C", (255, 160, 64)),
        ("Ground Tilt", f"X: {tilt_x} deg", (230, 100, 255))
    ]

    for i, (label, val, val_color) in enumerate(metrics):
        y = start_y + i * (row_h + spacing)
        draw.rectangle((10, y, width - 10, y + row_h), fill=(28, 37, 54), outline=(40, 53, 77))
        draw.text((20, y + 12), label, fill=(150, 170, 190))
        draw.text((200, y + 12), val, fill=val_color)

    disp.image(image)