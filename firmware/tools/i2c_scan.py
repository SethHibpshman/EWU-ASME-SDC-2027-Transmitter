"""
I2C Scan Tool
=============
Bring-up utility for the ASME SDC 2027 ESP-NOW Transmitter.
Scans the shared I2C bus and reports every device that answers,
labeling the ones expected on this board.

Run from IDE with the board powered (boost on).

Author: Seth Hibpshman
License: GNU GPL v3
"""

from machine import Pin, I2C

# I2C bus (same as main.py)
SCL_PIN = 42
SDA_PIN = 41
FREQ = 100000   # Slow for scanning, more forgiving of weak solder joints

KNOWN_DEVICES = {
    0x3C: "SSD1306 OLED",
    0x3D: "SSD1306 OLED (alt address)",
    0x75: "IP5306-I2C charger/boost",
}

EXPECTED = (0x3C, 0x75)


def scan():
    i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=FREQ)
    found = i2c.scan()

    print("I2C scan on SCL={}, SDA={} at {} Hz".format(SCL_PIN, SDA_PIN, FREQ))
    print("-" * 40)

    if not found:
        print("No devices found.")
        print("Check: board powered, pull-ups R8/R9 fitted, SDA/SCL not swapped.")
        return

    for addr in found:
        name = KNOWN_DEVICES.get(addr, "Unknown device")
        print("0x{:02X} ({:3d})  {}".format(addr, addr, name))

    print("-" * 40)
    missing = [a for a in EXPECTED if a not in found]
    if missing:
        for addr in missing:
            print("MISSING: 0x{:02X} {}".format(addr, KNOWN_DEVICES[addr]))
    else:
        print("All expected devices found.")


scan()