# ============================================================
# 🌍 EARTHQUAKE DETECTION USING MPU6050 + RASPBERRY PI PICO
# ============================================================

import sys
import machine
from machine import Pin, I2C, PWM
from imu import MPU6050
from time import sleep, ticks_ms
from math import atan2, sqrt, degrees, acos
import _thread

# === LED Indicator ===
LED = Pin("LED", Pin.OUT)
LED.on()  # LED ON indicates system is active

# === I2C Setup ===
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)

# === Settings ===
VIBRATION_THRESHOLD = 0.2       # g  → Minimum vibration spike
TILT_THRESHOLD = 1.0            # °  → Minimum tilt to confirm strong motion
PIEZO_THRESHOLD = 3.0           # mV → Minimum piezo response (derived from vibration)
INVINCIBILITY_DURATION = 0.5    # s  → Ignore startup transients
REQUIRED_CONSECUTIVE_SPIKES = 2 # Trigger alert only after this many consecutive spikes

start_time = ticks_ms()
prev_lin_a_mag = None
alert_triggered = False
consec_spike_count = 0  # counts consecutive spikes


# ============================================================
# 📊 Helper Functions
# ============================================================

def calculate_linear_acceleration(ax, ay, az):
    """Removes gravity (assumed ~1g on Z-axis) and returns linear acceleration magnitude."""
    lin_ax = ax
    lin_ay = ay
    lin_az = az - 1.0
    lin_a_mag = sqrt(lin_ax**2 + lin_ay**2 + lin_az**2)
    return lin_ax, lin_ay, lin_az, lin_a_mag

def calculate_tilt(ax, ay, az):
    """Calculates tilt angle (degrees) relative to the calibrated resting orientation."""
    dot = ax * ref_ax + ay * ref_ay + az * ref_az
    mag1 = sqrt(ax**2 + ay**2 + az**2)
    mag2 = sqrt(ref_ax**2 + ref_ay**2 + ref_az**2)
    cos_theta = dot / (mag1 * mag2)
    cos_theta = max(-1, min(1, cos_theta))
    return degrees(acos(cos_theta))

def calculate_piezo_mv(lin_a_mag):
    """Converts acceleration magnitude to an equivalent Piezo sensor voltage (mV)."""
    relative = max(0, lin_a_mag - piezo_baseline)
    return relative * 800  # Scale factor: 0.2g → ~300mV


# === Calibration ===
CALIBRATION_SAMPLES = 100
sum_ax = sum_ay = sum_az = 0

for _ in range(CALIBRATION_SAMPLES):
    sum_ax += imu.accel.x
    sum_ay += imu.accel.y
    sum_az += imu.accel.z
    sleep(0.001)

ref_ax = sum_ax / CALIBRATION_SAMPLES
ref_ay = sum_ay / CALIBRATION_SAMPLES
ref_az = sum_az / CALIBRATION_SAMPLES

# === Piezo baseline calibration ===
PIEZO_CALIBRATION_SAMPLES = 100
sum_lin_a_mag = 0

for _ in range(PIEZO_CALIBRATION_SAMPLES):
    ax = imu.accel.x
    ay = imu.accel.y
    az = imu.accel.z
    _, _, _, lin_a_mag = calculate_linear_acceleration(ax, ay, az)
    sum_lin_a_mag += lin_a_mag
    sleep(0.001)

piezo_baseline = sum_lin_a_mag / PIEZO_CALIBRATION_SAMPLES


# ============================================================
# 💡 LED DOUBLE FLOW ANIMATION (Parallel Thread)
# ============================================================

flow_speed = 0.1        # seconds each step
brightness = 40000      # 0–65535 (LED brightness)
gap = 1                 # number of LEDs between the two “on” LEDs

# Define LED pins (GP2–GP7)
led_pins = [2, 3, 4, 5, 6, 7]
leds = [PWM(Pin(pin)) for pin in led_pins]

# Set PWM frequency for all LEDs
for led in leds:
    led.freq(1000)

def turn_off_all():
    """Turn off all LEDs safely"""
    for led in leds:
        led.duty_u16(0)

def led_flow():
    """Run double LED flowing animation continuously"""
    num_leds = len(leds)
    while True:
        for i in range(num_leds):
            turn_off_all()
            leds[i].duty_u16(brightness)
            second_index = (i + gap) % num_leds
            leds[second_index].duty_u16(brightness)
            sleep(flow_speed)

# Start LED animation in a separate thread
_thread.start_new_thread(led_flow, ())


# ============================================================
# 🚨 MAIN EARTHQUAKE DETECTION LOOP
# ============================================================

while True:
    ax = imu.accel.x
    ay = imu.accel.y
    az = imu.accel.z

    lin_ax, lin_ay, lin_az, lin_a_mag = calculate_linear_acceleration(ax, ay, az)
    tilt = calculate_tilt(ax, ay, az)
    piezo_mv = calculate_piezo_mv(lin_a_mag)

    if lin_a_mag > VIBRATION_THRESHOLD:
        SCALING_FACTOR = 1.5
        lin_a_mag = lin_a_mag * SCALING_FACTOR

    if (ticks_ms() - start_time) / 1000 > INVINCIBILITY_DURATION:
        if prev_lin_a_mag is not None:
            vib_change = abs(lin_a_mag - prev_lin_a_mag)
            if vib_change > VIBRATION_THRESHOLD and tilt > TILT_THRESHOLD and piezo_mv > PIEZO_THRESHOLD:
                consec_spike_count += 1
                if consec_spike_count >= REQUIRED_CONSECUTIVE_SPIKES and not alert_triggered:
                    print("ALERT,ALERT,ALERT")
                    alert_triggered = True
            else:
                consec_spike_count = 0
        prev_lin_a_mag = lin_a_mag

    if alert_triggered:
        print("\nSystem resetting in 5s...\n")
        sleep(5)
        alert_triggered = False
        consec_spike_count = 0
        prev_lin_a_mag = None
        start_time = ticks_ms()
        continue

    data_line = "{:.2f},{:.2f},{:.2f}".format(lin_a_mag, tilt, piezo_mv)
    print(data_line)
    machine.idle()
    sleep(0.05)