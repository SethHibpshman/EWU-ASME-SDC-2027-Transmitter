# IP5306 registers, battery voltage, soft power-off

class IP5306:
    self.pin = Pin

    def _read(self, reg):
        i2c.readfrom_mem(0x75, 0x00, 1)