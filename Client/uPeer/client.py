import random
import select
import socket
import string
import time

from Crypto.Cipher import AES

from keypair import KeyPair


class Client():

    def __init__(self, custom_key_pair: KeyPair | None, server_address_ip: str, server_port: int) -> None:
        # Set the server address as a tuple
        self.server_address = (server_address_ip, server_port)

        # Check if custom key pair is being used
        if custom_key_pair:
            self.client_key_pair = custom_key_pair
        else:
            self.client_key_pair = KeyPair()
            self.client_key_pair.add_keypair_from_files()

        # Create a TCP socket that will be used to communicate with the control server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def register(self, client_name: str) -> bool:
        if len(client_name) > 32:
            raise ValueError("Client name can be max length of 32 characters")

        # Connect to the control server
        self.server_socket.connect(self.server_address)

        # Register with the client name
        # See README.md for more information
        payload = 0x11.to_bytes(1, byteorder="little") + \
            self.client_key_pair.public_key_string.encode(
                "ascii") + client_name.encode("ascii")
        self.server_socket.send(payload)

        data = self.server_socket.recv(1)
        return len(data) and data[0] == 0
    
    def connect(self, remote_public_key: str) -> Connection | None:
        pass # TODO: Implement


if __name__ == "__main__":
    client = Client(None, "localhost", 8090)
    test = client.register("Minecraft server")
    print(test)
