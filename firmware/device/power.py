# IP5306 registers, battery voltage, soft power-off

from machine import Pin, ADC
from config import PIN_BATT, V_FULL, V_EMPTY

# FUEL GAUGE ########################
fuel = ADC(Pin(PIN_BATT), atten=ADC.ATTN_11DB)   # Setting up an ADC class for each pot and putting it in a list
fuel_val = fuel.read_u16()                       # 0 to 65535
DIVIDER = 2.0                                    # (R1 + R2) / R2

def batt_voltage():
    return round(fuel.read_uv() / 1000000 * DIVIDER, 2) # Convert uV to V, and undo the divider in software.
# Ideas to make this an average ^? To remove jittery results.

def batt_percent():
    v = batt_voltage()
    percent = (v - V_EMPTY) / (V_FULL - V_EMPTY) * 100
    return max(0, min(100, int(round(percent, 0))))


# class IP5306:
#     self.pin = Pin
#
#     def _read(self, reg):
#         i2c.readfrom_mem(0x75, 0x00, 1)