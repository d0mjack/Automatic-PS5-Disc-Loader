from machine import Pin, PWM
import time

# Set up the servo on Pin GP15
servo = PWM(Pin(15))
servo.freq(50)  # Standard frequency for servos


def set_angle(angle):
    # Map 0-180 degrees to the duty cycle (approx 1638 to 8192 for 16-bit)
    # 0 degrees = ~1.0ms pulse; 180 degrees = ~2.0ms pulse
    duty = int((angle / 180) * 6554 + 1638)
    servo.duty_u16(duty)


print("Starting back and forth motion...")

try:
    while True:
        # Move forward from 0 to 180
        for degree in range(0, 181, 5):
            set_angle(degree)
            time.sleep(0.05)

        # Move backward from 180 to 0
        for degree in range(180, -1, -5):
            set_angle(degree)
            time.sleep(0.05)

except KeyboardInterrupt:
    # Turn off the PWM signal when you stop the code
    servo.deinit()
    print("Motion stopped.")