import network
import socket
import time
from machine import Pin, ADC

# set up onboard led
led = Pin("LED", Pin.OUT)

state = "OFF"

# set up some variables with our wifi details, replace these with your Wi-Fi credentials
ssid = "FeliceOrbi"
password = "felicewifi123"


# this function connects the pico to a wifi network
def connect():
    # Sets up wireless module instance, turn on the wireless hardware, and then connect with our credentials
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    # We print the status of the connection here to help see whats going on
    while wlan.isconnected() == False:
        print("Connecting, please wait...")
        time.sleep(1)
    # Once it completes the while true loop, we will print out the Pico's IP on the network
    print("Connected! ip = ", wlan.ifconfig()[0])


# you can call this function to make the pico host its own wifi AP instead
def ap_setup():
    # Sets up wireless module instance, configures access point, then turns on Wi-Fi hardware
    ap = network.WLAN(network.AP_IF)
    ap.config(ssid=ssid, password=password)
    ap.active(True)
    # We print the status of the connection here to help see whats going on
    while ap.active() == False:
        print("Initialising access point...")
        time.sleep(1)

    # Once it completes the while true loop, we will print out the Pico's IP on the network, will default to 192.168.4.1
    print("AP is operational, ip = ", ap.ifconfig()[0])


# function to open a socket which is what the pico uses to allow other devices to send and recieve information with.
def open_socket():
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()

    # ADD THIS LINE: This tells the Pico to reuse the port immediately
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(address)
    s.listen(1)
    return (s)


# This defines the webpage to be served.
def webpage(state):
    # 1. Open the file
    with open("website.html", "r") as f:
        html = f.read()

    # 2. Replace the placeholder text with the actual state variable
    html = html.replace("{state}", state)

    return html


# start by either hosting ap or connecting to Wi-Fi
connect()
# ap_setup()
# and then open the socket
s = open_socket()

try:
    # this loop ensures the page is served everytime a client connects, not just once.
    while True:
        # this is a blocking call, the code will stop here until a client tries to connect
        client = s.accept()[0]
        # when a client does connect, it will send a request which we will store in a variable
        request = client.recv(1024)
        request = str(request)
        # this request comes through as a giant mess, this part gives us just /request?
        try:
            request = request.split()[1]
        # the pass is important because we cannot always split a request, this will prevent errors
        except IndexError:
            pass
        print(request)

        # here we use comparative logic to control the LED based on the request
        if request == "/on?":
            led.value(1)
            state = "ON"
        elif request == "/off?":
            led.value(0)
            state = "OFF"
        # then we recreate the html site with the updated states
        html = webpage(state)
        # This sends a http response header back to our client, some browsers might not work without this line. very technical.
        client.send("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n")
        client.send(html)
        # end by closing the client, will reopen again next loop.
        client.close()

# if we get an error, we will close the connection and let us know there was an error.
except OSError as e:
    client.close()
    print("Error: connection closed")