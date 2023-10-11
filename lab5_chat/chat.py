import socket
import threading
import json
import os

# Server configuration
HOST = '127.0.0.1' # Loopback address for localhost
PORT = 12345 # Port to listen on

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the specified address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}")


# Function to handle a client's messages
def handle_client(client_socket, client_address):

    print(f"Accepted connection to server: {client_address}")

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        message = json.loads(message)

        if not message:
            break  # Exit the loop when the client disconnects

        print(f"Received from {client_address}: {message}")

        if message["type"] == "connect":
            room = message["payload"]["room"]
            name = message["payload"]["name"]
            if room not in rooms_clients:
                rooms_clients[room] = []
                
                folder = room + "-" + "Folder"
                
                if not os.path.exists(folder):
                    rooms_folsers[room] = folder
                    os.mkdir(folder)
            rooms_clients[room].append([client_socket, name])
            rooms_folsers[room].append([folder])
            for client in rooms_clients[room]:
                if client[0] == client_socket:
                    return_message = {
                        "type": "connect_ack",
                        "payload": {
                            "message": f"Connected to the room: {message['payload']['room']}."
                        }
                    }
                    client[0].send(json.dumps(return_message).encode('utf-8'))
                else:
                    return_message = {
                        "type": "notification",
                        "payload": {
                            "message": f"{message['payload']['name']} has joined the room."
                        }
                    }
                    client[0].send(json.dumps(return_message).encode('utf-8'))


        if message["type"] == "message" and message["payload"]["room"] != "":
            room = message["payload"]["room"]
            name = message["payload"]["sender"]
            text = message["payload"]["text"]

            return_message = {
                "type": "message",
                "payload": {
                    "sender": name,
                    "room": room,
                    "text": text
                }
            }

            # Broadcast the message to all clients
            for client in rooms_clients[room]:
                if client[0] != client_socket:
                    client[0].send(json.dumps(return_message).encode('utf-8'))

        if message["type"] == "upload":
            room = message["payload"]["room"]
            name = message["payload"]["sender"]
            file_name = message["payload"]["file_name"]
            file_data = message["payload"]["file"]

            return_message = {
                "type": "notification_upload",
                "payload": {
                    "sender": name,
                    "room": room,
                    "file_name": file_name,
                    "file": file_data
                }
            }

            # Broadcast the message to all clients
            for client in rooms_clients[room]:
                if client[0] != client_socket:
                    client[0].send(json.dumps(return_message).encode('utf-8'))

            
    # Remove the client from the list
    clients.remove(client_socket)
    client_socket.close()


# dictionary of rooms and their clients
clients = []
rooms_clients = {}
rooms_folsers = {}








while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()