import socket

from keypair import KeyPair
import tools


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

        remote_ip, remote_port, local_port = tools.extract_port_and_ip_from_data(data)

        # -- TEST --
        print(remote_ip)
        print(f"rp {remote_port}")
        print(f"lp {local_port}")
        # -- TEST --

        # TODO: Implement

    def listen_for_connection(self, whitelist=None, blacklist=None):
        while True:
            # TODO: Change all recv to r, _, _ = select.select([socket], [], [])
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

            data = self.server_socket.recv(9)

            remote_ip, remote_port, local_port = tools.extract_port_and_ip_from_data(data)

            # -- TEST --
            print(remote_ip)
            print(f"rp {remote_port}")
            print(f"lp {local_port}")
            # -- TEST --
            
            # TODO: Return connection
            return


# -- TEST This is for testing --
if __name__ == "__main__":
    client = Client(None, "localhost", 8090)
    test = client.register("Minecraft server")
    print(client.client_key_pair.public_key_string)
    #client.listen_for_connection()
    client.connect("MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtZL5JoLRpERzLpukeaAU6wWKWclXCQmsxd04AtkcGdoMbHLfp2Ke3ysk0oTVq74W+boF0sXJ4SnAwRUOPP4VXsx3666FQHfDfDrxRxMt2pB7I818RIRATmVf53iNaVbs62qrpV8jEN2Y5eya1iEqRlaclbANw/pFArJ6naR0bxfR0nYAeXbw184Y+xcpVz/6brvjOF1RXA9lkZz/fWFku65RSTzqtJZoKXPYh+hOuuvkSYKC36+GVYxp48dnKduoKqcpLS5WRbt1B/MSIHXXEn6fLVdsiw4z2lA26CJLygCjjvIgbzee3OHYhQ8bYc2tStzhnrFwr5T/Wu8dnkrgDQIDAQAB");
    #client.connect("MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4niqYneX9ClHhJ6zwFsOYXu8xEbjyxyYVMwlAPCsiSDY17huoOejKj9DtktceCOfW6XavOr/7Xd7rgTPrs0UETxA9N7rda9gplh1MXwaQPFchQY2Wo4e/bmE1lk8xvpEywJKMfuAVQ879Yf7YzDkBXpxI/LGk+kcm6eSrnKeMyoI+dfh4Rt887BPZbkfVotooH7wqXZzSnAQVA4q840FjZxG+f5Z4v3AAe4vGfih/p3yW3dqk5fEGFAOfui74ypXfSbrErFENUOUTPkueWn/Hbt90xnaZDFqFANK2vZNmIKultvHyhfow3zACcSzNPMd5+P0Ikp//jH8y47bFBSdEQIDAQAB")
# -- TEST --
