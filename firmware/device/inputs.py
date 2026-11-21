"""
inputs.py
=========
The setup for all user input hardware.

Author: Seth Hibpshman
License: GNU GPL v3
"""

from machine import Pin, ADC
from config import PIN_AXES, PIN_POTS, BUTTON_PINS

# BUTTONS ###############################
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in BUTTON_PINS]   # Assigning a Pin class for each button then putting it in a list
btn_vals = [0] * len(buttons)                                  # A list containing the value of each button

# POTENTIOMETERS ########################
pots = [ADC(Pin(p), atten=ADC.ATTN_11DB) for p in PIN_POTS]    # Setting up a ADC class for each pot and putting it in a list
pot_vals = [p.read_u16() for p in pots]                        # 0 to 65535






