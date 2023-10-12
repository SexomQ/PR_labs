import socket
import threading
import json
import os
import base64

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

def create_connection_for_binary_transfer(client_socket, room, file_name):
    try:
        file_size = int(client_socket.recv(10).decode("utf-8").strip())
        received_size = 0
        with open(room + "-" + "Folder" + "/" + file_name, "wb") as file:
            while received_size < file_size:
                file_data = client_socket.recv(1024)
                if not file_data:
                    break
                file.write(file_data)
                received_size += len(file_data)
        print("File has been received successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to handle a client's messages
def handle_client(client_socket, client_address):

    print(f"Accepted connection to server: {client_address}")

    while True:
        got_message = client_socket.recv(1024)

    
        user_message = got_message.decode('utf-8')
        message = json.loads(user_message)

        if not message:
            break  # Exit the loop when the client disconnects

        print(f"Received from {client_address}: {message}")

        if message["type"] == "connect":
            request_type = "json"
            room = message["payload"]["room"]
            name = message["payload"]["name"]
            if room not in rooms_clients:
                rooms_clients[room] = []
                
            folder = room + "-" + "Folder"
            user_folder = name + "-" + "Folder"

            if not os.path.exists(folder):
                rooms_folsers[room] = folder
                os.mkdir(folder)
            
            elif folder not in rooms_folsers:
                rooms_folsers[room] = folder

            if not os.path.exists(user_folder):
                users_folders[name] = user_folder
                os.mkdir(user_folder)

            elif folder not in users_folders:
                users_folders[name] = user_folder
            
            rooms_clients[room].append([client_socket, name])
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


        elif message["type"] == "message" and message["payload"]["room"] != "":
            request_type = "json"
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

        elif message["type"] == "upload":
            if message["payload"]["file_type"] == "txt":
                request_type = "json"
                room = message["payload"]["room"]
                name = message["payload"]["sender"]
                file_name = message["payload"]["file_name"]
                file_data = message["payload"]["file"]

                if file_data == "EOF":
                    return_message = {
                        "type": "notification_upload",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": file_name,
                            "file": file_data,
                            "message": f"{message['payload']['sender']} has uploaded a file: {message['payload']['file_name']}.",
                            "file_type": "txt"
                        }
                    }

                    # Broadcast the message to all clients
                    for client in rooms_clients[room]:
                        if client[0] != client_socket:
                            client[0].send(json.dumps(return_message).encode('utf-8'))
                else:
                    file_data = base64.b64decode(message["payload"]["file"] + "=" * ((4 - len(message["payload"]["file"]) % 4) % 4))
                    
                    print(rooms_folsers.get(room))
                    uploaded_file = open(rooms_folsers.get(room) + "/" + file_name, "wb") 
                    uploaded_file.write(file_data)
                    uploaded_file.close()

            elif message["payload"]["file_type"] == "png":
                room = message["payload"]["room"]
                name = message["payload"]["sender"]
                file_name = message["payload"]["file_name"]
                file_data = message["payload"]["file"]
                    
                if file_data == "":
                    create_connection_for_binary_transfer(client_socket, room, file_name)
                    
                    return_message = {
                        "type": "notification_upload",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": file_name,
                            "file": file_data,
                            "message": f"{message['payload']['sender']} has uploaded a file: {message['payload']['file_name']}.",
                            "file_type": "png"
                        }
                    }

                    # Broadcast the message to all clients
                    for client in rooms_clients[room]:
                        if client[0] != client_socket:
                            client[0].send(json.dumps(return_message).encode('utf-8'))


        elif message["type"] == "download":
            room = message["payload"]["room"]
            name = message["payload"]["sender"]
            file_name = message["payload"]["file_name"]

            if os.path.exists(rooms_folsers.get(room) + "/" + file_name):
                file = open(rooms_folsers.get(room) + "/" + file_name, "rb")

                if file_name.split(".")[1] == "txt":
                    file_data = file.read(1024)
                    while file_data:
                        return_message = {
                            "type": "request_download",
                            "payload": {
                                "sender": name,
                                "room": room,
                                "file_name": file_name,
                                "file": str(base64.b64encode(file_data))[2:-1]
                            }
                        }

                        client_socket.send(json.dumps(return_message).encode('utf-8'))
                        file_data = file.read(1024)

                    return_message = {
                            "type": "request_download",
                            "payload": {
                                "sender": name,
                                "room": room,
                                "file_name": file_name,
                                "file": "EOF"
                            }
                        }
                    client_socket.send(json.dumps(return_message).encode('utf-8'))
                    file.close()

                elif file_name.split(".")[1] == "png":
                    return_message = {
                        "type": "request_download",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": file_name,
                            "file": ""
                        }
                    }
                    client_socket.send(json.dumps(return_message).encode('utf-8'))

                    try:
                        path = rooms_folsers.get(room) + '/' + file_name

                        file = open(path, 'rb') # open the file in binary mode
                        file_size = os.path.getsize(path)
                        client_socket.send(f"{file_size:<10}".encode('utf-8'))
                        
                        while True:
                            file_data = file.read(1024)
                            if not file_data:
                                break
                            client_socket.send(file_data)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    finally:
                        file.close()

                    

                    
            
            else:
                return_message = {
                        "type": "request_download",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": file_name,
                            "file": "#"
                        }
                    }
                client_socket.send(json.dumps(return_message).encode('utf-8'))

        
    # Remove the client from the list
    clients.remove(client_socket)
    client_socket.close()


# dictionary of rooms and their clients
clients = []
rooms_clients = {}
rooms_folsers = {}
users_folders = {}
request_type = "json"







while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()