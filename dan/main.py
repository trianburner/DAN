from microdot import Microdot, Response, redirect
from microdot.session import Session, with_session
import network
from webserver import webserver
from dan_backend import initialize_backend
from sx1262 import SX1262

initialize_backend()

# TODO recall settings from file on boot

# Set WiFi options for hosted softAP
SSID = "DAN_dev_A"
PASSWORD = "123456789"

# Set country
rp2.country('US')

# Disable WiFi power-saving
# ap.config(pm = 0xa11140)

# Configure AP settings for softAP network
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Wait until the AP has started before continuing
while ap.active == False:
        pass

# Set static IP address
ap.ifconfig(('192.168.1.2', '255.255.255.0', '192.168.1.1', '8.8.8.8'))

print("--Access point active")
print("--SSID: " + SSID)
print(ap.ifconfig())



# Start web server at port 80
if __name__ == '__main__':
    webserver.start_server()