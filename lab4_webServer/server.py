# lsof -i :8080
# list of open files

import socket
import signal
import sys
from time import sleep
import threading
import json

# define the server's IP and port
HOST = "127.0.0.1"
PORT = 8080

# create a socket object ip4, tcp
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the specified host and port
server_socket.bind((HOST, PORT))

# listen for incoming connections
server_socket.listen(5)
print(f"[*] Listening as {HOST}:{PORT}")


# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


# function to handle clients' requests
def handle_request(client_socket):
    # Receive and print the client's request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    # Parse the request to get the HTTP method and path
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]
    next_id = path[-1]

    # Initialize the response content and status code
    response_content = ''
    status_code = 200

    # Define a simple routing mechanism
    if path == '/':
        response_content = '''<h1>Hello, World!</h1>
            <a href="/about">About</a>
            <a href="/contacts">Contacts</a>
            <a href="/products">Products</a>
            <a href="/">Home</a>
        '''
    elif path == '/about':
        response_content = '<h1> This is about page </h1>'

    elif path == '/contacts':
        response_content = '<h1> This is contacts page </h1>'

    elif path == '/products':
        with open('products.json', "r") as json_file:
            data = json.load(json_file)

            response = "<h2> This are the products </h2> \n"
            for i in range(len(data["products"])):
                prod = data["products"][i]
                response = response + f'''<a href="/products/{i}"> {prod["name"]} </a> <br>'''
                response_content = response

    elif path == f'/products/{next_id}':
        with open('products.json', "r") as json_file:
            data = json.load(json_file)

            if int(next_id) < len(data["products"]) :
                prod = data["products"][int(next_id)]

                response = "<h2> This is the item </h2> \n"
                name = prod["name"]
                author = prod["author"]
                price = prod["price"]
                description = prod["description"]

                response_content = f'''
                    <p id="name"> {name} </p> <br>
                    <p id="author"> {author} </p> <br>
                    <p id="price"> {price} </p> <br>
                    <p id="description"> {description} </p> <br>
                    '''
            else : 
                response_content = '<p>404 Not Found</p>'

    else:
        response_content = '404 Not Found'
        status_code = 404

    # Prepare the HTTP response
    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))

    # Close the client socket
    client_socket.close()


while True:
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    try:
        # Handle the client's request in a separate thread
        handle_request(client_socket)
    except KeyboardInterrupt:
        # Handle Ctrl+C interruption here (if needed)
        pass


# while True:
#     # Accept incoming client connections
#     client_socket, client_address = server_socket.accept()
#     print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

#     # Create a thread to handle the client's request
#     client_handler = threading.Thread(target=handle_request, args=(client_socket,))
#     client_handler.start()