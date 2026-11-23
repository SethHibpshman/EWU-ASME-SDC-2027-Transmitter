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
    full = ip.is_full()
    if charging is None:
        state = "UNKNOWN"
    elif charging or full:
        state = "FULL" if full else "CHARGING"
    else:
        state = "ON BATTERY"
    oled.text(state, 0, 20)

import math
import inputs

def draw_inputs_screen():
    """Draw every input: pots as 270-degree gauges, buttons as two diamonds
    of circles (filled = pressed), sticks as boxes with a moving dot.
    Reads fresh values from inputs.py. Does not clear or show the screen."""

    # Read fresh values (raw 0 to 65535 -> usable ranges)
    axes = [(j.read_u16() - 32768) / 32768 for j in inputs.joys]   # lx, ly, rx, ry: -1 to 1
    pots = [p.read_u16() / 65535 for p in inputs.pots]             # 0 to 1
    btns = [b.value() == 0 for b in inputs.buttons]                # True = pressed (active low)

    def gauge(cx, cy, r, value):
        # Arc from 135 deg (bottom-left) sweeping 270 deg to bottom-right
        start, sweep = 135, 270
        prev = None
        for deg in range(start, start + sweep + 1, 15):
            a = math.radians(deg)
            pt = (cx + round(r * math.cos(a)), cy + round(r * math.sin(a)))
            if prev:
                oled.line(prev[0], prev[1], pt[0], pt[1], 1)
            prev = pt
        # Needle
        a = math.radians(start + sweep * max(0.0, min(1.0, value)))
        oled.line(cx, cy,
                  cx + round((r - 3) * math.cos(a)),
                  cy + round((r - 3) * math.sin(a)), 1)
        oled_gfx.fill_circle(cx, cy, 1, 1)

    def diamond(cx, cy, states):
        # Order: top, right, bottom, left (clockwise from top)
        spots = ((0, -8), (8, 0), (0, 8), (-8, 0))
        for (dx, dy), pressed in zip(spots, states):
            if pressed:
                oled_gfx.fill_circle(cx + dx, cy + dy, 3, 1)
            else:
                oled_gfx.circle(cx + dx, cy + dy, 3, 1)

    def stick(x, y, size, sx, sy):
        oled.rect(x, y, size, size, 1)
        c = size // 2
        oled.pixel(x + c, y + c, 1)                      # Center mark
        travel = c - 3                                   # Keep the dot inside the box
        dx = x + c + round(max(-1.0, min(1.0, sx)) * travel)
        dy = y + c + round(max(-1.0, min(1.0, sy)) * travel)   # +y is up on screen
        oled.fill_rect(dx - 1, dy - 1, 3, 3, 1)          # 3x3 dot

    # Top row: pots in the corners, button diamonds between them
    gauge(12, 13, 11, pots[0])
    diamond(42, 13, btns[0:4])
    diamond(85, 13, btns[4:8])
    gauge(115, 13, 11, pots[1])

    # Bottom row: joysticks
    stick(6, 32, 30, axes[0], axes[1])
    stick(92, 32, 30, axes[2], axes[3])