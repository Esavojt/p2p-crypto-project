import socket

from keypair import KeyPair


class Client():
    def __init__(self, custom_key_pair: KeyPair | None, server_address_ip: str, server_port: int) -> None:
        # Set the server address as a tuple
        self.server_address = (server_address_ip, server_port)

        # Check if custom key pair is being used
        if custom_key_pair is not None:
            # Assert that custom_key_pair is instance of KeyPair
            assert(isinstance(custom_key_pair, KeyPair))

            # Use custom keypair
            self.client_key_pair = custom_key_pair
        else:
            # Import keypair from files
            self.client_key_pair = KeyPair()
            self.client_key_pair.import_file_keys()

        # Assert that all key strings exist
        assert(self.client_key_pair.private_key_string and self.client_key_pair.public_key_string)

        # Create a TCP socket that will be used to communicate with the control server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def register(self, client_name: str) -> bool:
        if len(client_name) > 32:
            raise ValueError("Client name can be max length of 32 characters")

        # Connect to the control servery
        self.server_socket.connect(self.server_address)

        # Register with the client name
        # See README.md for more information
        payload = 0x11.to_bytes(1, byteorder="little") + \
            self.client_key_pair.public_key_string.encode("ascii") + \
            client_name.encode("ascii")

        # Send data to server
        self.server_socket.send(payload)

        # Receive Acknowledgement from the server
        data = self.server_socket.recv(1)

        return len(data) > 0 and data[0] == 0x0

    def connect(self, remote_public_key: str):  # -> Connection | None:
        # Make the connection payload
        payload = 0x12.to_bytes(1, byteorder="little") + \
            self.client_key_pair.public_key_string.encode("ascii") + \
            remote_public_key.encode("ascii")

        # Send the payload to the server
        self.server_socket.send(payload)

        # Receive Acknowledgement or Connection setup from server
        data = self.server_socket.recv(9)

        # If server sent nack
        if data[0] == 0x01:
            # Return None to indicate that connection cannot be established
            return None

        # Server sent Connection setup

        # Receive and make remote ip in format "192.168.1.1"
        remote_ip = str(int.from_bytes(data[1:2], byteorder="little")) + "." + \
            str(int.from_bytes(data[2:3], byteorder="little")) + "." + \
            str(int.from_bytes(data[3:4], byteorder="little")) + "." + \
            str(int.from_bytes(data[4:5], byteorder="little"))

        print(remote_ip)
        # TODO: Implement

    def listen_for_connection(self, whitelist=None, blacklist=None):
        while True:
            data = self.server_socket.recv(393)

            if data[0] != 0x13:
                self.server_socket.close()
                raise ConnectionError("Received something else then connection establishment message!")

            remote_address = data[1:].decode("ascii")

            print(f"Received connection from {remote_address}")

            # Check if whitelist is supplied and if remote address is not in whitelist
            if whitelist is not None and remote_address not in whitelist:
                # Refuse connection
                self.server_socket.send(0x01.to_bytes(1, byteorder="little"))
                print("Address isn't in whitelist, refusing.")
                continue

            # Check if blacklist is supplied and if remote address is not in blacklist
            if blacklist is not None and remote_address in blacklist:
                # Refuse connection
                self.server_socket.send(0x01.to_bytes(1, byteorder="little"))
                print("Address is in blacklist, refusing.")
                continue

            print("Accepting!")
            self.server_socket.send(0x00.to_bytes(1, byteorder="little"))

            # TODO: Return connection
            data = self.server_socket.recv(9)

            # Convert the supplied IPv4 address from raw bytes to str
            remote_ip = str(int.from_bytes(data[1:2], byteorder="little")) + "." + \
                str(int.from_bytes(data[2:3], byteorder="little")) + "." + \
                str(int.from_bytes(data[3:4], byteorder="little")) + "." + \
                str(int.from_bytes(data[4:5], byteorder="little"))

            # -- TEST --
            local_port = 12
            remote_port = 12
            # -- TEST --
            print(remote_ip)
            return


# -- TEST This is for testing --
if __name__ == "__main__":
    client = Client(None, "localhost", 8090)
    test = client.register("Minecraft server")
    client.connect("MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlryQ9BlDIUIApbL931aXK6uAdvWNYHg8isot0aQSxly1EH98jYI7TD9J\
    IEu0LHZQs0Vcjjziu3MjgvL+d9yniyH7y63woyiE1F88dDs8PBSYL34ot3brIkLXkHLrihwqTl5nTo+46JXhfDrKZX/r8foPL3ZE9apYLTNa+5W0H3dA\
    CQkTv9W+ZjRAa/JNM701vfolWWYyUS7dngwC2BmLe9mFo491K+yWkWwefq79OGSjGyNd+duWL05hZbLmA/vnVN7s2hSQYpDjo5VECgVOM08zdoZ9ZYH5\
    xj0cL6Al5bGpVK47ggtQ8dRz7b+/q/zMkzCGU8PpI9CP6R3FD+KoSwIDAQAB")
# -- TEST --
