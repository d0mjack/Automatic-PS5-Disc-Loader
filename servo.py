from machine import PWM, Pin
class Servo:
    def __init__(self, pin_id, min_us=544, max_us=2400, min_deg=0, max_deg=180, freq=50):
        self.pwm = PWM(Pin(pin_id))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.min_deg = min_deg
        self.max_deg = max_deg
    def write(self, deg):
        if deg < self.min_deg: deg = self.min_deg
        if deg > self.max_deg: deg = self.max_deg
        us = self.min_us + (deg - self.min_deg) * (self.max_us - self.min_us) / (self.max_deg - self.min_deg)
        self.pwm.duty_ns(int(us * 1000))
