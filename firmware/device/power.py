"""
power.py
=========
Power monitoring & management through the IP5306 chip and a fuel gauge.

Author: Seth Hibpshman
License: GNU GPL v3
"""
# IP5306 registers, battery voltage, soft power-off

from collections import OrderedDict
from machine import Pin, ADC
from time import sleep_ms
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
CHARGE_CURRENT = 0x0A   # 1.05 A (I = 0.05 + 0.1 * value), USB side

# Every setting the chip has: name: (register, start_bit, width)
# OrderedDict keeps this order when printing.
FIELDS = OrderedDict((
    # SYS_CTL0 (0x00)
    ("button_off",        (0x00, 0, 1)),   # 1 = button can power down (no effect in standby)
    ("standby",           (0x00, 1, 1)),   # 1 = 5V always on, settings kept ("keep-on")
    ("auto_load_on",      (0x00, 2, 1)),   # 1 = turn on when a load is plugged in
    ("charger_enable",    (0x00, 4, 1)),   # 1 = charger on
    ("boost_enable",      (0x00, 5, 1)),   # 1 = 5V output on, 0 = board powers off
    # SYS_CTL1 (0x01)
    ("low_batt_cutoff",   (0x01, 0, 1)),   # 1 = shut off at 3.0 V
    ("boost_after_vin",   (0x01, 2, 1)),   # 1 = keep 5V on when USB is unplugged
    ("short_press_boost", (0x01, 5, 1)),   # 1 = short press turns 5V on
    ("boost_off_clicks",  (0x01, 7, 1)),   # press type that turns 5V off (sources disagree, test it)
    # SYS_CTL2 (0x02)
    ("light_load_time",   (0x02, 2, 2)),   # 0 = 8 s, 1 = 32 s, 2 = 16 s, 3 = 64 s
    ("long_press_time",   (0x02, 4, 1)),   # 0 = 2 s, 1 = 3 s
    # Charger
    ("charge_stop_v",     (0x20, 0, 2)),   # fine-tune full-charge stop voltage (00 or 01 recommended)
    ("charge_uv_loop",    (0x21, 2, 3)),   # VOUT floor while charging: 4.45 V + 0.05 V per step
    ("charge_done_ma",    (0x21, 6, 2)),   # 0 = 200, 1 = 400, 2 = 500, 3 = 600 mA
    ("v_compensation",    (0x22, 0, 2)),   # 0 = none, 1 = 14 mV, 2 = 28 mV, 3 = 42 mV
    ("battery_voltage",   (0x22, 2, 2)),   # 0 = 4.2 V (leave it), 1 = 4.3, 2 = 4.35, 3 = 4.4
    ("cc_loop_vin",       (0x23, 5, 1)),   # 1 = measure charge current on USB side, 0 = battery side
    ("charge_current",    (0x24, 0, 5)),   # I = 0.05 + 0.1 * value A, max 0x13 (1.95 A)
    # Status (read-only)
    ("charging",          (0x70, 3, 1)),   # 1 = charging
    ("full",              (0x71, 3, 1)),   # 1 = fully charged
    ("light_load",        (0x72, 2, 1)),   # 1 = load is light
))

READ_ONLY = ("charging", "full", "light_load")

class IP5306:
    """Driver for the IP5306-I2C charger/boost chip on the shared I2C bus.
    Every read returns None, and every write returns False, if the chip is asleep."""

    def __init__(self):
        """Use the shared I2C bus and KEY_CTRL pin from config."""
        self.i2c = config.i2c
        self.addr = config.IP5306_ADDR
        self.key = Pin(config.PIN_KEY_CTRL, Pin.OUT, value=0)

    def __str__(self):
        """Every setting by name, so print(ip) shows the whole chip."""
        lines = []
        for name in FIELDS:
            lines.append("{:18} {}".format(name, self.get(name)))
        return "\n".join(lines)

    # LOW LEVEL: WHOLE REGISTERS ##########
    def read_reg(self, reg):
        """Read one register (all 8 bits). None if the chip doesn't answer."""
        try:
            return self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        except OSError:
            return None

    def write_reg(self, reg, value):
        """Write one register (all 8 bits). True if it worked."""
        try:
            self.i2c.writeto_mem(self.addr, reg, bytes([value]))
            return True
        except OSError:
            return False

    def update_bits(self, reg, mask, value):
        """Change only the bits in mask, leave the rest untouched. True if it worked."""
        old = self.read_reg(reg)
        if old is None:
            return False
        new = (old & ~mask) | (value & mask)
        if new == old:
            return True
        return self.write_reg(reg, new)

    # MID LEVEL: NAMED SETTINGS ###########
    def get(self, name):
        """Read a setting by name from FIELDS. None if the chip doesn't answer."""
        reg, start, width = FIELDS[name]
        value = self.read_reg(reg)
        if value is None:
            return None
        return (value >> start) & ((1 << width) - 1)

    def set(self, name, value):
        """Change a setting by name from FIELDS. True if it worked."""
        if name in READ_ONLY:
            raise ValueError(name + " is read-only")
        reg, start, width = FIELDS[name]
        mask = ((1 << width) - 1) << start
        return self.update_bits(reg, mask, value << start)

    # HIGH LEVEL: WHAT MAIN.PY USES #######
    def configure(self):
        """Boot settings. The chip forgets them whenever it loses power.
        Lines marked CHANGE differ from the chip's defaults. Lines marked
        ENSURE already match the defaults but are set so nothing is assumed."""
        return all((
            # CHANGE
            self.set("light_load_time", 3),   # 32 s -> 64 s grace before light-load auto-off
            self.set("charge_done_ma", 0),    # 500 mA -> 200 mA, fuller charge
            self.set("charge_current", CHARGE_CURRENT),  # 2.25 A -> 1.05 A, cooler, USB-port friendly
            # ENSURE
            self.set("standby", 0),           # default 0: SW9 double-press can turn the board off
            self.set("button_off", 1),        # default 1: SW9 allowed to power down
            self.set("boost_after_vin", 1),   # default 1: no dropout when USB is unplugged
            self.set("low_batt_cutoff", 1),   # default 1: 3.0 V hardware backup cutoff
            self.set("v_compensation", 2),    # default 2: +28 mV, vendor recommendation for 4.2 V
        ))

    def is_charging(self):
        """True / False, or None if unknown."""
        v = self.get("charging")
        return None if v is None else v == 1

    def is_full(self):
        """True / False, or None if unknown."""
        v = self.get("full")
        return None if v is None else v == 1

    def is_load_light(self):
        """True / False, or None if unknown."""
        v = self.get("light_load")
        return None if v is None else v == 1

    def button_event(self):
        """Returns 'short', 'long', 'double' or None, and clears the flag."""
        for name, event in (("double_pressed", "double"),
                            ("long_pressed", "long"),
                            ("short_pressed", "short")):
            if self.get(name) == 1:
                self.set(name, 1)             # writing 1 clears the flag
                return event
        return None

    def wake(self):
        """Hold KEY low for 500 ms through Q1 to wake I2C (it sleeps in standby)."""
        if self.key is None:
            return
        self.key.value(1)
        sleep_ms(500)
        self.key.value(0)
        sleep_ms(50)

    def power_off(self):
        """Double-tap KEY through Q1 to turn the board off (same as double-pressing SW9)."""
        if self.key is None:
            return False
        for i in range(2):
            self.key.value(1)         # Q1 on, KEY pulled low (press)
            sleep_ms(150)
            self.key.value(0)         # release
            sleep_ms(150)
        return True