"""
display.py
=========
Handling user feedback, including the OLED and the LED.

Author: Seth Hibpshman
License: GNU GPL v3
"""

from machine import Pin
from config import OLED_W, OLED_H, i2c, PIN_LED
import ssd1306
import gfx
import power

# INITIALIZATION ########################
# LED
led = Pin(PIN_LED, Pin.OUT)
# OLED
oled     = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)
oled_gfx = gfx.GFX(OLED_W, OLED_H, oled.pixel, oled.hline, oled.vline)

# FUNCTIONS #############################
def draw_centered(text, center_x, y):
    width = len(text) * 8
    x = center_x - (width // 2)
    oled.text(text, x, y)

def draw_right_aligned(text, right_x, y):
    oled.text(text, right_x - len(text)*8, y)

def draw_battery_screen(ip):
    percent = power.batt_percent()

    # Battery Icon
    oled_gfx.rect(99, 0, 27, 15, 1)
    oled_gfx.rect(126, 3, 2, 9, 1)   # Positive terminal

    # Battery Bars
    if percent > 25:
        oled_gfx.fill_rect(128 - 27, 2, 5, 11, 1)
    if percent > 50:
        oled_gfx.fill_rect(128 - 21, 2, 5, 11, 1)
    if percent > 75:
        oled_gfx.fill_rect(128 - 15, 2, 5, 11, 1)
    if percent > 90:
        oled_gfx.fill_rect(128 - 9, 2, 5, 11, 1)

    # Voltage
    oled.text(f"{power.batt_percent()} %", 0, 0)
    oled.text(f"{power.batt_voltage()} V", 0, 10)

    # Status
    charging = ip.is_charging()
    if charging is None:
        state = "UNKNOWN"
    elif charging:
        state = "CHARGING"
    else:
        state = "ON BATTERY"
    oled.text(state, 0, 20)