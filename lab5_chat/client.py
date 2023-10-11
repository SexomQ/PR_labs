import json
import socket
import threading
import os 

# server config
HOST = "127.0.0.1"  # Localhost
PORT = 12345  # port to listen to

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the socket to the specified host and port
client_socket.connect((HOST, PORT))

# # listen for incoming connections
# client_socket.listen()

print(f"[*] Listening as {HOST}:{PORT}")


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        message = json.loads(message)
        if not message:
            break  # Exit the loop when the server disconnects
        
        if message["type"] == "connect_ack":
            print(f"{message['payload']['message']}")
        
        if message["type"] == "notification":
            print(f"{message['payload']['message']}")
        
        if message["type"] == "message":
            print(f"{message['payload']['sender']}: {message['payload']['text']}")


# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Thread will exit when the main program exits
receive_thread.start()

name = ""
room = ""
while True:
    message = input()

    if message.lower() == 'exit':
        break

    if message.lower() == 'connect':
        room = input("enter room: ")
        name = input("enter name: ")

        message_json = {
         "type": "connect",
         "payload": {
             "name": name,
             "room": room
            }
         }
        client_socket.send(json.dumps(message_json).encode('utf-8'))

    if message.lower() == "upload":
        file_name = input("Enter file path: ")
        path = os.path.basename(file_name)

        file = open(file_name, "rb")

        file_data = file.read(1024)
        while file_data:
            message_json = {
                "type": "upload",
                "payload": {
                    "sender": name,
                    "room": room,
                    "file_name": os.path.split(path)[1],
                    "file": file_data
                }
            }

            client_socket.send(json.dumps(message_json).encode('utf-8'))
            file_data = file.read(1024)
        file.close()

    else:
        mess = {
            "type": "message",
            "payload": {
                "sender": name,
                "room": room,
                "text": message
            }
        }

        # Send the message to the server
        client_socket.send(json.dumps(mess).encode('utf-8'))

# Close the client socket when done
client_socket.close()