from microdot.microdot import Microdot, Response, send_file
from microdot.websocket import with_websocket
import json
import asyncio
import dan_backend as dan

app = Microdot()
MAX_PINNED_MESSAGES = 10
MAX_MESSAGE_HISTORY = 30
# store messages and current clients
messages = []
pinned_messages = []
client_usernames = {}

@app.route('/')
def index(request):
    return send_file('/webserver/templates/index.html')

@app.route('/settings')
def settings(request):
    return send_file('/webserver/templates/settings.html')

@app.route('/static/<path:path>')
def static(request, path):
    return send_file(f'/webserver/static/{path}')

@app.route('/ws')
@with_websocket
async def chat(request, ws):
    # add new client to set
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
            for message in messages:
                await ws.send(json.dumps(message))
                
            #users that just connected will get a copy of currently pinned messages
            for pinned_message in pinned_messages:
                await ws.send(json.dumps(pinned_message))
            
            __message_append(system_message)
            
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
                __message_append(message)
                
                await _send_to_all_clients(message)
            
            elif data['type'] == 'pin_message':
                pinned_message = {
                    'type': 'pinned_message',
                    'username': data['username'],
                    'text': data['text']
                }
                if pinned_messages not in pinned_messages:
                    __pinned_message_append(pinned_message)
                    # sends pinned messages to every user
                    await _send_to_all_clients(pinned_message)
            
            elif data['type'] == 'unpin_message':
                remove_text_search = data['text'].split(":")[1].strip()
                username = data['text'].split(":")[0]
                try:
                    pinned_messages.remove(next(filter(lambda x: x['text'] == remove_text_search and x['username'] == username, pinned_messages)))
                    # create unpinned message object
                    unpin_message = {
                        'type': 'unpin_message',
                        'text': data['text']
                    }
                    #updates all users of what messages were pinned
                    await _send_to_all_clients(unpin_message)
                except ValueError:
                    print("Pinned message not found, ignore")
   
    # websocket is closed/error, prompt user leaving, and remove from client set
    except Exception:
        if username:
            leave_message = {
                'type': 'system',
                'text': f'{username} has left the chat'
            }
            __message_append(leave_message)
            # send leave message to remaining clients
            await _send_to_all_clients(leave_message)
        
        
        #removes entry of user when they disconnect
        if ws in client_usernames:
            del client_usernames[ws]
        
        #updates all users of whose currently online after a user leaves
        await _send_user_list_to_all_clients()

# helper function for sending messages to all connected clients
async def _send_to_all_clients(msg):
  json_msg = json.dumps(msg)
  dan.send(json_msg)
  for client in client_usernames:
    try:
      await client.send(json_msg)
    except Exception:
      del client_usernames[client]

#helper function for sending list of currently connected users
async def _send_user_list_to_all_clients():
    user_list = list(client_usernames.values())

    user_list_message = {
        'type': 'user_list',
        'users': user_list
    }

    await _send_to_all_clients(user_list_message)

def __message_append(msg):
    messages.append(msg)
    if len(messages) > MAX_MESSAGE_HISTORY:
        messages.pop(0)

def __pinned_message_append(msg):
    pinned_messages.append(msg)
    if len(pinned_messages) > MAX_PINNED_MESSAGES:
        pinned_messages.pop(0)

def start_server():
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print(f'Server error: {e}')
        
if __name__ == '__main__':
    start_server()