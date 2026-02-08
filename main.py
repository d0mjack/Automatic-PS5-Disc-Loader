import network
import time
import urequests

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
    while not wlan.isconnected():
        print("Connecting, please wait...")
        time.sleep(1)
    # Once it completes the while true loop, we will print out the Pico's IP on the network
    print("Connected! IP = ", wlan.ifconfig()[0])

try:
    connect()
    site = "https://api.ipify.org"

    print("query: ", site)
    r = urequests.get(site)

    print(r.json)
    r.close()

except OSError as e:
    print("Error: connection closed")
    r.close()
