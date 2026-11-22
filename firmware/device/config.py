"""
config.py
=========
Every pin number, address, and tuning constant for the transmitter.
No other file should contain a raw pin number. If the hardware changes,
this is the only file that changes.

Author: Seth Hibpshman
License: GNU GPL v3
"""

from machine import I2C, Pin

# I2C BUS (shared: OLED + IP5306) #######
I2C_ID = 0
PIN_SCL = 42
PIN_SDA = 41
I2C_FREQ = 400000
i2c = I2C(scl=Pin(PIN_SCL), sda=Pin(PIN_SDA), freq=I2C_FREQ)

# OLED ##################################
OLED_ADDR = 0x3C
OLED_W = 128
OLED_H = 64

# IP5306-I2C ############################
IP5306_ADDR = 0x75
PIN_KEY_CTRL = 40          # Drives Q1, pulse high to "press" the power key
PIN_IP5306_INT = None      # Set to 39 once R5 is fitted (INT voltage confirmed safe)
CHARGE_CURRENT_REG = 0x0A  # 0x24 bits 4:0, 0x0A = 1.05 A from USB

# BATTERY ###############################
PIN_BATT = 8               # Fuel gauge pin
V_EMPTY = 3.2
V_FULL = 4.2

# ANALOG INPUTS (ADC1 only) #############
# Order matters: lx, ly, rx, ry
PIN_AXES = (1, 2, 4, 5)
PIN_POTS = (6, 7)

# BUTTONS (active low, internal pull-ups)
BUTTON_PINS = (11, 12, 13, 14, 15, 16, 17, 18)

# STATUS LED ############################
PIN_LED = 38

# CALIBRATION ###########################
#Calibrate all ADC and voltage divider

# LINK (ESP-NOW) ########################
#Setup for ESP-NOW stuff