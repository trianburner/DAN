from microdot import Microdot, Response, send_file
from microdot.websocket import with_websocket
import json
import asyncio


app = Microdot()

# store messages and current clients
messages = []
clients = set()
client_usernames = {}
pinned_messages = []

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
            client_usernames[ws] = username
            
            # system message that user has joined
            system_message = {
                'type': 'system',
                'text': f'{username} has joined the chat'
            }
            
            # send message history to newly connected
            for message in messages[-10:]:
                await ws.send(json.dumps(message))

            #users that just connected will get a copy of currently pinned messages
            for pinned_message in pinned_messages:
                await ws.send(json.dumps(pinned_message))
            
            messages.append(system_message)
            
            # send joined message to every connected client
            await _send_to_all_clients(system_message)


            #updates all users of who's currently online
            await _send_user_list_to_all_clients()

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
            
            elif data['type'] == 'pin_message':
                #create pinned message object
                pinned_message = {
                    'type': 'pinned_message',
                    'username': username,
                    'text': data['text']
                }
                #stores all pinned messages
                pinned_messages.append(pinned_message)
                #sends pinned messages to every user
                await _send_to_all_clients(pinned_message)
            
            elif data['type'] == 'unpin_message':
                remove_text = data['text']
                leftover_pinned = []

                #go through all pinned messages except for the one we don't want
                for msg in pinned_messages:
                    if msg['text'] != remove_text:
                        #keep all messages that are not the one we want removed
                        leftover_pinned.append(msg)
                
                pinned_messages[:] = leftover_pinned

                #create unpinned message object
                unpin_message = {
                    'type': 'unpin_message',
                    'text': remove_text
                }
                #updates all users of what messages were pinned
                await _send_to_all_clients(unpin_message)
   
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
        
        #removes entry of user when they disconnect
        if ws in client_usernames:
            del client_usernames[ws]
        
        #updates all users of whose currently online after a user leaves
        await _send_user_list_to_all_clients()

# helper function for sending messages to all connected clients
async def _send_to_all_clients(msg):
  for client in clients:
    try:
      await client.send(json.dumps(msg))
    except Exception:
      clients.remove(client)

#helper function for sending list of currently connected users
async def _send_user_list_to_all_clients():
    user_list = list(client_usernames.values())

    user_list_message = {
        'type': 'user_list',
        'users': user_list
    }
    await _send_to_all_clients(user_list_message)

def start_server():
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print(f'Server error: {e}')
        
if __name__ == '__main__':
    start_server()