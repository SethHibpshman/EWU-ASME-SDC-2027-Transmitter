import power
from time import sleep

ip = power.IP5306()
results = []

def check(name, ok):
    results.append((name, ok))
    print("{:40} {}".format(name, "PASS" if ok else "FAIL"))

print("\n=== IP5306 CLASS TEST ===\n")

# 1. Chip responds
check("chip answers (read_reg not None)", ip.read_reg(0x00) is not None)

# 2. Dump everything before changes
print("\n--- before configure ---")
print(ip)

# 3. configure() applies and reads back correctly
check("configure() returns True", ip.configure())
check("light_load_time == 3 (64 s)", ip.get("light_load_time") == 3)
check("charge_done_ma == 0 (200 mA)", ip.get("charge_done_ma") == 0)
check("charge_current == 10 (1.05 A)", ip.get("charge_current") == power.CHARGE_CURRENT)
check("standby == 0", ip.get("standby") == 0)
check("button_off == 1", ip.get("button_off") == 1)
check("low_batt_cutoff == 1", ip.get("low_batt_cutoff") == 1)

# 4. set() changes ONLY its own bits (reserved bits untouched)
before = ip.read_reg(0x02)
ip.set("long_press_time", 1)                     # harmless setting
after = ip.read_reg(0x02)
check("set() changed long_press_time", ip.get("long_press_time") == 1)
check("set() left other bits alone", (before & ~0b00010000) == (after & ~0b00010000))
ip.set("long_press_time", 0)                     # put it back
check("set() restored long_press_time", ip.get("long_press_time") == 0)

# 5. Read-only fields refuse writes
try:
    ip.set("charging", 0)
    check("read-only field blocked", False)
except ValueError:
    check("read-only field blocked", True)

# 6. Status methods return real booleans (USB plugged in)
check("is_charging() is True (USB in)", ip.is_charging() is True)
check("is_full() returns a bool", isinstance(ip.is_full(), bool))
check("is_load_light() returns a bool", isinstance(ip.is_load_light(), bool))

# 7. Light-load check for Option A (30 s)
print("\n--- light-load watch, 30 s (radio/OLED should be running) ---")
light_count = 0
for _ in range(15):
    if ip.is_load_light():
        light_count += 1
    sleep(2)
check("load never light (Option A is safe)", light_count == 0)

# 8. Dump everything after changes
print("\n--- after configure ---")
print(ip)

# Summary
passed = sum(1 for _, ok in results if ok)
print("\n=== {} / {} passed ===".format(passed, len(results)))