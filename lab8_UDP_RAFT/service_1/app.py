# With help from Vasile Papaluta


from flask import Flask
import os
import dotenv
from models.electro_scooter import ElectroScooter
from models.database import db
from flask_swagger_ui import get_swaggerui_blueprint
import socket
import requests
import json
import threading
import time

service_info = {
    "host" : "127.0.0.1",
    "port" : 5001,
}

class RAFTFactory:
    def __init__(self,
                 service_info : dict,
                 udp_host : str = "127.0.0.1",
                 udp_port : int = 4444,
                 udp_buffer_size : int = 1024,
                 num_followers : int = 1):
        '''
            The constructor of the RAFTFactory.
        :param service_info: dict
            The credentials of the service including the host, port and hte degree.
        :param udp_host: str, default = '127.0.0.1'
            The host used for UDP connection.
        :param udp_port: int, default = 4444
            The the port used for UDP connection.
        :param udp_buffer_size: int, default = 1024
            The size in bytes of the messages.
        :param num_followers: int
            The number of followers in the partition.
        '''
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.udp_buffer_size = udp_buffer_size
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.service_info = service_info
        # The number of messages to end the process of election is equal to
        # number of follower * 2
        self.min_num_msgs = num_followers * 2
        # Trying to bind the UDP connection.
        try:
            # If the binding is successful then then the service is declared as the partition leader.
            self.udp_socket.bind((self.udp_host, self.udp_port))
            self.role = "leader"

            # Starting to gather the information about the followers as they connect using UDP.
            self.followers = []
            count_of_msgs = 0
            while True:
                # Reading the message and the address from connection.
                message, address = self.udp_socket.recvfrom(self.udp_buffer_size)
                # If the sender accept that the service will be the leader then the leader sends back it's
                # HTTP credentials.
                if message.decode() == "Accept":
                    data = json.dumps(self.service_info)
                    count_of_msgs += 1
                    self.udp_socket.sendto(str.encode(data), address)
                else:
                    # After accepting and getting the leader's HTTP credentials the followers send his credentials
                    # which the leader is saving.
                    message = message.decode()
                    count_of_msgs += 1
                    follower_data = json.loads(message)
                    if follower_data not in self.followers:
                        self.followers.append(follower_data)
                if count_of_msgs >= self.min_num_msgs:
                    break
        except:
            # If the service is failing to bind to the UDP connection then it becomes a follower.
            self.role = "follower"

            # Sending the "Accept" message and getting the leader's data.
            self.leader_data = self.send_accept("Accept")

            # Sending back the it's credentials.
            self.send_accept(self.service_info)
        self.udp_socket.close()

    def send_accept(self, msg):
        '''
            This function is used by Followers to get and send data to/from Leader.
        :param msg: str or dict.
            The message to send to the Leader.
        '''
        # If the message is a string then the Follower is sending the message and is getting the
        # message back from Leader.
        if type(msg) is str:
            bytes_to_send = str.encode(msg)
            self.udp_socket.sendto(bytes_to_send, (self.udp_host, self.udp_port))
            msg_from_server = self.udp_socket.recvfrom(self.udp_buffer_size)[0]
            return json.loads(msg_from_server.decode())
        else:
            # If the message is a dictionary then the Follower is just sending the message to the Leader.
            str_dict = json.dumps(msg)
            bytes_to_send = str.encode(str_dict)
            self.udp_socket.sendto(bytes_to_send, (self.udp_host, self.udp_port))

def create_app(db):
    SWAGGER_URL="/swagger"
    API_URL="/static/swagger.json"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Access API'
        }
    )

    app = Flask(__name__)
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///scooter1.db'

    db.init_app(app)
    return app

if __name__ == '__main__':
    server = RAFTFactory(service_info)
    if server.role == "leader":
        print("I am the leader")
        print(server.followers)
    else:
        print("I am a follower")
        print(server.leader_data)

    
        
    app = create_app(db)
    import routes
    app.run(debug=True, port=service_info["port"], host=service_info["host"])