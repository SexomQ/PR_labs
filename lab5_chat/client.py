import json
import socket
import threading
import os 
import base64

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
        mess = client_socket.recv(1024).decode('utf-8')
        message = json.loads(mess)
        if not message:
            break  # Exit the loop when the server disconnects
        
        if message["type"] == "connect_ack":
            print(f"{message['payload']['message']}")
        
        if message["type"] == "notification":
            print(f"{message['payload']['message']}")
        
        if message["type"] == "message":
            print(f"{message['payload']['sender']}: {message['payload']['text']}")
        
        if message["type"] == "notification_upload":
            print(f"{message['payload']['message']}")

        if message["type"] == "request_download":
            if message["payload"]["file"] == "#":
                print(f"File {message['payload']['file_name']} does not exist")
            elif message["payload"]["file"] == "EOF":
                print(f"{message['payload']['file_name']} downloaded")
            else:
                file_name = message["payload"]["file_name"]
                file = open(file_name, "wb")
                file.write(base64.b64decode(message["payload"]["file"] + "=" * ((4 - len(message["payload"]["file"]) % 4) % 4)))
                file.close()


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

    elif message.lower() == 'connect':
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

    elif message.lower().split(":")[0] == "upload":
        if message.split(".")[1] == "txt":
            file_name = message.split(" ")[1]
            if os.path.exists(file_name):
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
                            "file": str(base64.b64encode(file_data))[2:-1],
                            "file_type": "txt"
                        }
                    }

                    client_socket.send(json.dumps(message_json).encode('utf-8'))
                    file_data = file.read(1024)
                message_json = {
                        "type": "upload",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": os.path.split(path)[1],
                            "file": "EOF",
                            "file_type": "txt"
                        }
                    }
                client_socket.send(json.dumps(message_json).encode('utf-8'))
                file.close()
            else:
                print(f"File {file_name} does not exist")
        elif message.split(".")[1] == "png":
            file_name = message.split(" ")[1]
            if os.path.exists(file_name):
                path = os.path.basename(file_name)

                # request to change the server to work with bin
                message_json = {
                        "type": "upload",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "file_name": os.path.split(path)[1],
                            "file": "",
                            "file_type": "png"
                        }
                    }
                
                client_socket.send(json.dumps(message_json).encode('utf-8'))

                try:
                    file = open(file_name, 'rb')
                    file_size = os.path.getsize(file_name)
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
                print(f"File {file_name} does not exist")

    elif message.lower().split(":")[0] == "download":
        file_name = message.split(" ")[1]
        message_json = {
                    "type": "download",
                    "payload": {
                        "sender": name,
                        "room": room,
                        "file_name": file_name
                    }
                }
        client_socket.send(json.dumps(message_json).encode('utf-8'))

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