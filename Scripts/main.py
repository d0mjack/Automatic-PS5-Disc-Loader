# main.py
import network
import socket
import time
from machine import Pin, PWM

# ── Hardware & Servo setup ────────────────────────────────────────────────
VERTICAL_PIN = 0
HORIZONTAL_PIN = 1

vertical_servo = PWM(Pin(VERTICAL_PIN))
vertical_servo.freq(50)
horizontal_servo = PWM(Pin(HORIZONTAL_PIN))
horizontal_servo.freq(50)

def set_servo_angle(servo, angle):
    angle = max(0, min(180, angle))
    duty_us = 500 + (2000 * angle) // 180
    servo.duty_u16(duty_us * 65535 // 20000)

LEVEL_ANGLES = {1: 10, 2: 50, 3: 90, 4: 130, 5: 170}  # ← calibrate these!
RETRACT_ANGLE = 5
PUSH_ANGLE = 95

current_level = 1
is_loaded = False
status_msg = "Ready"

def load_sequence():
    global is_loaded, status_msg
    if is_loaded:
        status_msg = "Already loaded"
        return
    set_servo_angle(vertical_servo, LEVEL_ANGLES[current_level])
    time.sleep(1.2)
    set_servo_angle(horizontal_servo, PUSH_ANGLE)
    time.sleep(0.9)
    is_loaded = True
    status_msg = f"Loaded disc (level {current_level})"

def unload_sequence():
    global is_loaded, status_msg
    if not is_loaded:
        status_msg = "Nothing loaded"
        return
    set_servo_angle(horizontal_servo, RETRACT_ANGLE)
    time.sleep(0.9)
    set_servo_angle(vertical_servo, LEVEL_ANGLES[1])
    is_loaded = False
    current_level = 1
    status_msg = "Disc unloaded"

def set_level(level):
    global current_level, status_msg
    if level in LEVEL_ANGLES:
        set_servo_angle(vertical_servo, LEVEL_ANGLES[level])
        time.sleep(1.1)
        current_level = level
        status_msg = f"Level {level} selected"
    else:
        status_msg = f"Invalid level: {level}"

# ── WiFi ───────────────────────────────────────────────────────────────────
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('FeliceOrbi', 'felicewifi123')

print("Connecting to WiFi")
while not wlan.isconnected():
    print("Connecting...")          # new line each time
    time.sleep(1)
print("Connected! IP:", wlan.ifconfig()[0])

# ── Simple route handlers ─────────────────────────────────────────────────
def handle_root():
    try:
        with open('website.html', 'r') as f:
            html = f.read()
        html = html.replace('{state}', 'OFF')           # keep if you still have LED
        html = html.replace('{level}', str(current_level))
        html = html.replace('{status}', status_msg)
        html = html.replace('{loaded}', 'Yes' if is_loaded else 'No')
        return html
    except OSError:
        return "<h1>Error: website.html not found</h1>"

def handle_select(params):
    level = int(params.get('level', 0))
    set_level(level)
    return f"Level set to {current_level}"

def handle_load(_):
    load_sequence()
    return status_msg

def handle_unload(_):
    unload_sequence()
    return status_msg

# ── Route table ────────────────────────────────────────────────────────────
routes = {
    '/':          (handle_root, 'text/html'),
    '/select':    (handle_select, 'text/plain'),
    '/load':      (handle_load,   'text/plain'),
    '/unload':    (handle_unload, 'text/plain'),
    # Add more later, e.g. '/status' → JSON
}

# ── HTTP Server ────────────────────────────────────────────────────────────
def parse_path_and_query(request_line):
    parts = request_line.split(' ')
    if len(parts) < 2:
        return '/', {}
    full_path = parts[1]
    if '?' not in full_path:
        return full_path, {}
    path, query = full_path.split('?', 1)
    params = {}
    for pair in query.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            params[k] = v
    return path, params

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(3)
print("Server listening on port 80")

# ... your WiFi connect code above ...

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # explicit type helps sometimes
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # this is the key line

s.bind(addr)
s.listen(5)  # queue up to 5 pending connections
print("Server listening on http://", wlan.ifconfig()[0])

while True:
    try:
        conn, client_addr = s.accept()
        request = conn.recv(1024).decode('utf-8', 'ignore')
        if not request:
            conn.close()
            continue

        first_line = request.split('\n', 1)[0]
        path, params = parse_path_and_query(first_line)

        handler, content_type = routes.get(path, (lambda _: "Not found", 'text/plain'))
        body = handler(params)

        response = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\nConnection: close\n\n{body}"
        conn.sendall(response.encode())
        conn.close()
    except Exception as e:
        print("Error:", e)
        try:
            conn.close()
        except:
            pass