"""
LAB 3: IoT Smart Gate Control
ESP32 + MicroPython + BlynkLib (WebSocket – device shows Online)

Hardware:
  - IR Sensor   : OUT → D14, GND → GND, VCC → 5V
  - Servo Motor : Signal (Yellow) → D13, VCC (Red) → 5V, GND (Brown) → GND
  - TM1637      : CLK → D17, DIO → D16, VCC → 5V, GND → GND

Blynk Virtual Pins:
  V0  - IR status label       (String: "Detected" / "Not Detected")
  V1  - Servo slider          (Integer 0–180, manual control)
  V2  - Detection counter     (Integer)
  V3  - Manual override switch (0 = Auto, 1 = Manual)
"""

import network
import time
from machine import Pin, PWM
import BlynkLib
from tm1637 import TM1637

# ── User configuration ────────────────────────────────────────────────────────
WIFI_SSID  = "Robotic WIFI"
WIFI_PASS  = "rbtWIFI@2025"
BLYNK_AUTH = "dRYD1uwuUag6iexHzca1tUZYGlPQFu-M"
BLYNK_API   = "http://blynk.cloud/external/api"
# ─────────────────────────────────────────────────────────────────────────────

# ── Pin numbers ───────────────────────────────────────────────────────────────
IR_PIN     = 14
SERVO_PIN  = 13
TM_CLK_PIN = 17
TM_DIO_PIN = 16
# ─────────────────────────────────────────────────────────────────────────────

# ── Hardware init ─────────────────────────────────────────────────────────────
ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)   # 0 = object present, 1 = clear

servo_pwm = PWM(Pin(SERVO_PIN), freq=50)

def angle_to_duty(angle):
    min_duty = int(0.5 / 20 * 1023)
    max_duty = int(2.5 / 20 * 1023)
    return int(min_duty + (max_duty - min_duty) * angle / 180)

def set_servo(angle):
    servo_pwm.duty(angle_to_duty(angle))

set_servo(0)

tm = TM1637(clk_pin=TM_CLK_PIN, dio_pin=TM_DIO_PIN, brightness=7)
tm.show_digit(0)
# ─────────────────────────────────────────────────────────────────────────────

# ── Wi-Fi ─────────────────────────────────────────────────────────────────────
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("WiFi connected!", wifi.ifconfig())
# ─────────────────────────────────────────────────────────────────────────────

# ── Blynk ─────────────────────────────────────────────────────────────────────
blynk = BlynkLib.Blynk(BLYNK_AUTH, insecure=True)

@blynk.on("connected")
def blynk_connected():
    print("Blynk connected!")
    blynk.virtual_write(0, "Not Detected")
    blynk.virtual_write(2, detection_count)

# V1: Servo slider (manual mode only)
@blynk.on("V1")
def v1_handler(value):
    if manual_mode:
        angle = max(0, min(180, int(float(value[0]))))
        print("[Blynk] Slider ->", angle, "deg")
        set_servo(angle)

# V3: Manual override switch
@blynk.on("V3")
def v3_handler(value):
    global manual_mode
    manual_mode = bool(int(value[0]))
    print("[Blynk] Mode ->", "MANUAL" if manual_mode else "AUTO")
    if not manual_mode:
        set_servo(0)
# ─────────────────────────────────────────────────────────────────────────────

# ── State ─────────────────────────────────────────────────────────────────────
detection_count = 0
manual_mode     = False
last_ir_state   = 1
# ─────────────────────────────────────────────────────────────────────────────

GATE_OPEN_ANGLE  = 90
GATE_CLOSE_ANGLE = 0
OPEN_DURATION_MS = 3000
BLYNK_INTERVAL   = 500

last_blynk_update = time.ticks_ms()
print("Lab 3 running...")

while True:
    blynk.run()

    now      = time.ticks_ms()
    ir_state = ir.value()

    # ── Auto mode: IR falling edge → open gate ────────────────────────────────
    if not manual_mode:
        if ir_state == 0 and last_ir_state == 1:
            detection_count += 1
            print("[IR] Object detected! Count =", detection_count)

            tm.show_digit(detection_count)
            set_servo(GATE_OPEN_ANGLE)
            print("[Gate] Open")

            blynk.virtual_write(0, "Detected")
            blynk.virtual_write(2, detection_count)

      # Hold open, keep Blynk alive
            open_start = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), open_start) < OPEN_DURATION_MS:
                blynk.run()
                time.sleep_ms(50)

            set_servo(GATE_CLOSE_ANGLE)
            print("[Gate] Closed")

            # Wait for object to leave before next detection
            while ir.value() == 0:
                blynk.run()
                time.sleep_ms(50)
            time.sleep_ms(300)   # debounce

            last_ir_state = 1
            continue

        elif ir_state == 1 and last_ir_state == 0:
            blynk.virtual_write(0, "Not Detected")

    last_ir_state = ir_state

    # ── Periodic heartbeat to keep widgets fresh ──────────────────────────────
    if time.ticks_diff(now, last_blynk_update) >= BLYNK_INTERVAL:
        blynk.virtual_write(0, "Detected" if ir_state == 0 else "Not Detected")
        blynk.virtual_write(2, detection_count)
        last_blynk_update = now

    time.sleep_ms(20)
