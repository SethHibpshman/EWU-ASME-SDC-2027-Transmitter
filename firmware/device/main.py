"""
ASME SDC 2027 ESP-NOW Transmitter
=================================
A MicroPython-based handheld transmitter for the ASME SDC 2027 robot.
Handles joystick, potentiometer, and button input, ESP-NOW wireless
control with telemetry, OLED status display, IP5306 battery charging
and power management, and fail-safe link loss detection.

Hardware:
    - ESP32-S3-DevKitC-1 N16R8 microcontroller (MicroPython)
    - SSD1306 128x64 OLED via I2C (SDA=41, SCL=42, addr 0x3C)
    - IP5306-I2C charger/boost on shared I2C bus (addr 0x75)
    - IP5306 interrupt on Pin 39, soft power key on Pin 40
    - Left joystick: X=1, Y=2
    - Right joystick: X=4, Y=5
    - Potentiometers on Pins 6 and 7
    - Battery voltage sense on Pin 8 (100k/100k divider)
    - Push buttons on Pins 11-18 (active low, internal pull-ups)
    - Status LED on Pin 38
    - Expansion header: GPIO 9, 10, 21, 48, UART0 TX=43, RX=44
    - Native USB on Pins 19/20 (REPL and programming via J2)
    - Single 18650 Li-ion cell, USB-C charging

Classes:
    None

Author: Seth Hibpshman
Firmware Validation: Kailyyie-Madison Scholz
License: GNU GPL v3
"""

from machine import Pin, I2C, PWM, ADC
from time import sleep, ticks_ms, ticks_diff
import config
import ssd1306
import gfx
from display import draw_centered, oled
import inputs
import power


def input_update():
    for i, btn in enumerate(inputs.buttons):
        inputs.btn_vals[i] = btn.value()
    for i, pot in enumerate(inputs.pots):
        inputs.pot_vals[i] = pot.read_u16()
    for i, joy in enumerate(inputs.joys):
        inputs.joy_vals[i] = joy.read_u16()
    power.fuel_val = power.fuel.read_u16()

# Test code
# while True:
#     sleep(1)
#     input_update()
#     draw_centered('Hello World!',64,10)
#     oled.show()

    #display.led.value(1)
    #print(inputs.btn_vals)
    #print(inputs.pot_vals)
    #print(inputs.joy_vals)
    #print(f'Battery Voltage: {power.batt_voltage()} which is {power.batt_percent()}%.')

ip = power.IP5306()
print(ip.read_reg(0x70))
print(ip.is_charging())
print(ip.is_full())
print(ip.is_load_light())