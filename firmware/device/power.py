"""
power.py
=========
Power monitoring & management through the IP5306 chip and a fuel gauge.

Author: Seth Hibpshman
License: GNU GPL v3
"""
# IP5306 registers, battery voltage, soft power-off

from machine import Pin, ADC
import config

# FUEL GAUGE ############################
fuel = ADC(Pin(config.PIN_BATT), atten=ADC.ATTN_11DB)   # Setting up an ADC class for each pot and putting it in a list
fuel_val = fuel.read_u16()                       # 0 to 65535
DIVIDER = 2.0                                    # (R1 + R2) / R2

def batt_voltage():
    return round(fuel.read_uv() / 1000000 * DIVIDER, 2) # Convert uV to V, and undo the divider in software.
# Ideas to make this an average ^? To remove jittery results.

def batt_percent():
    v = batt_voltage()
    percent = (v - config.V_EMPTY) / (config.V_FULL - config.V_EMPTY) * 100
    return max(0, min(100, int(round(percent, 0))))

# IP5306-I2C ############################
# registers
REG_SYS_CTL0      = 0x00   # boost, charger, keep-on, button-off
REG_SYS_CTL1      = 0x01   # button behavior, 3.0 V cutoff
REG_SYS_CTL2      = 0x02   # light-load auto-off delay
REG_CHG_CTL1      = 0x21   # charge-done current
REG_CHG_CURRENT   = 0x24   # charge current
REG_CHARGE_STATUS = 0x70   # bit 3: charging
REG_FULL_STATUS   = 0x71   # bit 3: full
REG_LIGHT_LOAD    = 0x72   # bit 2: light

class IP5306:
    """Driver for the IP5306-I2C charger/boost chip on the shared I2C bus."""

    def __init__(self):
        """Store the shared I2C bus and the chip's address from config."""
        self.i2c = config.i2c
        self.addr = config.IP5306_ADDR

    def __str__(self):
        """Text shown when the object is printed."""
        return f"Test"

    def read_reg(self, reg):
        """Read one register (all 8 bits) and return it as an integer."""
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def read_bit(self, reg, bit):
        """Read one bit of a register. Returns 0 or 1."""
        return (self.read_reg(reg) >> bit) & 1

    def write_reg(self, reg, value):
        """Write one register (all 8 bits). True if it worked."""
        try:
            self.i2c.writeto_mem(self.addr, reg, bytes([value]))
            return True
        except OSError:
            return False

    def update_bits(self, reg, mask, value):
        """Change only the bits in mask. True if it worked."""
        old = self.read_reg(reg)
        if old is None:
            return False
        new = (old & ~mask) | (value & mask)
        if new == old:
            return True
        return self.write_reg(reg, new)

    def is_charging(self):
        """True if the battery is charging (register 0x70, bit 3)."""
        return self.read_bit(REG_CHARGE_STATUS, 3) == 1

    def is_full(self):
        """True if the battery is fully charged (register 0x71, bit 3)."""
        return self.read_bit(REG_FULL_STATUS, 3) == 1

    def is_load_light(self):
        """True if the output load is light, the condition that can trigger auto-off (register 0x72, bit 2)."""
        return self.read_bit(REG_LIGHT_LOAD, 2) == 1