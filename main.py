from microdot import Microdot, Response, redirect
from microdot.session import Session, with_session
import network

# TODO recall settings from file on boot

# Set WiFi options for hosted softAP
SSID = "DAN_dev_A"
PASSWORD = "123456789"

# Set country
rp2.country('US')

# Disable WiFi power-saving
ap.config(pm = 0xa11140)

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
print(ap.ifconfig() + "\n")

# TODO Move these to files
BASE_TEMPLATE = '''<!doctype html>
<html>
  <head>
    <title>DAN</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <h1>Login to DAN</h1>
    {content}
  </body>
</html>'''

LOGGED_OUT = '''<p>You are not logged in.</p>
<form method="POST">
  <p>
    Username:
    <input name="username" autofocus />
  </p>
  <input type="submit" value="Submit" />
</form>'''

LOGGED_IN = '''<p>Hello <b>{username}</b>!</p>
<form method="POST" action="/logout">
  <input type="submit" value="Logout" />
</form>'''

# Create web server
app = Microdot()
Session(app, secret_key='top-secret')
Response.default_content_type = 'text/html'

# Define response to GET at root directory
@app.get('/')
@app.post('/')
@with_session
async def index(req, session):
    username = session.get('username')
    # Store session username after login
    if req.method == 'POST':
        username = req.form.get('username')
        session['username'] = username
        session.save()
        return redirect('/')
    # If logged out, send logged out page
    if username is None:
        return BASE_TEMPLATE.format(content=LOGGED_OUT)
    # If logged in, send logged in page with username
    else:
        return BASE_TEMPLATE.format(content=LOGGED_IN.format(
            username=username))

# Handle logout button press
@app.post('/logout')
@with_session
async def logout(req, session):
    session.delete()
    return redirect('/')

# Start web server at port 80
if __name__ == '__main__':
    app.run(port = 80)