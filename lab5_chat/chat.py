import socket
import threading

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
    accepted_dict = {     
        "type": "connect_ack",
        "payload": {
            "message": f"Connected to the room: {client_address}."
        }
    }

    print(f"Accepted connection : {accepted_dict}")

    final_mess = accepted_dict
    for client in clients:
            # if client != client_socket:
            client.send(final_mess.encode('utf-8'))

    print(f"Accepted connection : {accepted_dict}")

    while True:
        message = client_socket.recv(1024).decode('utf-8').to_dict()
        if not message:
            break  # Exit the loop when the client disconnects

        print(f"Received from {client_address}: {message}")

        if message["type"] == "message":
            final_mess = message
            
        if message["type"] == "connect":
            final_mess = {
                "type": "notification",
                "payload": {
                    "message": f"{message['payload']['message']} has joined the room."
                }
            }

        

        # Broadcast the message to all clients
        for client in clients:
            # if client != client_socket:
            client.send(final_mess.encode('utf-8'))

    # Remove the client from the list
    clients.remove(client_socket)
    client_socket.close()


clients = []








while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()