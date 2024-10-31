from microdot import Microdot, Response, send_file
from microdot.websocket import with_websocket
import json
import asyncio


app = Microdot()

# store messages and current clients
messages = []
clients = set()

@app.route('/')
def index(request):
    return send_file('static/index.html')

@app.route('/static/<path:path>')
def static(request, path):
    return send_file(f'static/{path}')

@app.route('/ws')
@with_websocket
async def chat(request, ws):
    # add new client to set
    clients.add(ws)
    username = None

    try:
        # wait for initial join message with username
        data = json.loads(await ws.receive())
        if data['type'] == 'join':
            username = data['username']
            
            # system message that user has joined
            system_message = {
                'type': 'system',
                'text': f'{username} has joined the chat'
            }
            messages.append(system_message)
            
            # send message history to newly connected
            for message in messages[-10:]:
                await ws.send(json.dumps(message))
            
            # send joined message to every connected client
            await _send_to_all_clients(system_message)

        while True:
            data = json.loads(await ws.receive())
            if data['type'] == 'message':
                # Create message object
                message = {
                    'type': 'message',
                    'username': username,
                    'text': data['text']
                }
                
                # store message
                messages.append(message)
                if len(messages) > 20:  # keep only last 20 messages
                    messages.pop(0)
                await _send_to_all_clients(message)
   
    # websocket is closed/error, prompt user leaving, and remove from client set
    except Exception:
        if username:
            leave_message = {
                'type': 'system',
                'text': f'{username} has left the chat'
            }
            messages.append(leave_message)
            # send leave message to remaining clients
            await _send_to_all_clients(leave_message)
        clients.remove(ws)

# helper function for sending messages to all connected clients
async def _send_to_all_clients(msg):
  for client in clients:
    try:
      await client.send(json.dumps(msg))
    except Exception:
      clients.remove(client)
  
def start_server():
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print(f'Server error: {e}')
        
if __name__ == '__main__':
    start_server()