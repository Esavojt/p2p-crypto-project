from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import os
import re


class KeyPair():
    private_key = None
    public_key = None

    private_key_string = None
    public_key_string = None

    def __init__(self) -> None:
        """
        Init function not supplied because importing keys is done by the following functions.
        """
        pass

    def import_file_keys(self) -> None:
        """
        This method imports keys from local files, if keys don't exist, it regenerates a new keypair
        """

        # Check if a folder exist
        if not os.path.isdir("keys"):
            os.mkdir("keys")

        # Check if key pair files don't exist
        if not os.path.isfile(os.path.join("keys", "private_key")) or not os.path.isfile(os.path.join("keys", "public_key")):
            print("Klíčový pár neexistuje, regenerujeme!")

            # Generate key pair
            key = RSA.generate(2048)
            self.private_key = key
            self.public_key = key.publickey()

            # Save private key to a file at ./keys/private_key
            file_out = open(os.path.join("keys", "private_key"), "wb")
            file_out.write(self.private_key.exportKey())
            file_out.close()

            # Save public key to a file at ./keys/public_key
            file_out = open(os.path.join("keys", "public_key"), "wb")
            file_out.write(self.public_key.export_key())
            file_out.close()

        else:
            # Load public key from a file
            public_key_file = open(os.path.join("keys", "public_key"), "r")
            self.public_key = RSA.import_key(public_key_file.read())
            public_key_file.close()

            # Load private key from a file
            private_key_file = open(os.path.join("keys", "private_key"), "r")
            self.private_key = RSA.import_key(private_key_file.read())
            private_key_file.close()

        # Trim the ---- START PUBLIC KEY ---- and ---- END PUBLIC KEY ---- padding
        # and save it to public/private_key_string
        public_key_string = self.public_key.export_key().decode("utf-8").replace("\n", "")
        self.public_key_string = re.sub(
            "-+[A-Z ]+-+", "", public_key_string)

        private_key_string = self.private_key.export_key().decode("utf-8").replace("\n", "")
        self.private_key_string = re.sub(
            "-+[A-Z ]+-+", "", private_key_string)

    def import_custom_keys(self, public_key: str, private_key: str) -> None:
        """
        This method imports keypair from supplied parameters
        """

        # Import public key
        self.public_key = RSA.import_key(
            "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----")

        # Import private key
        self.private_key = RSA.import_key(
            "-----BEGIN PRIVATE KEY-----\n" + private_key + "\n-----END PRIVATE KEY-----")

        # Trim the ---- START PUBLIC KEY ---- and ---- END PUBLIC KEY ---- padding
        public_key_string = self.public_key.export_key().decode("utf-8").replace("\n", "")
        self.public_key_string = re.sub(
            "-+[A-Z ]+-+", "", public_key_string)

        private_key_string = self.private_key.export_key().decode("utf-8").replace("\n", "")
        self.private_key_string = re.sub(
            "-+[A-Z ]+-+", "", private_key_string)

    def encrypt(self, buffer: bytes) -> bytes:
        """
        This method encrypts the buffer using the public key
        Function throws ValueError when the public key isn't supplied
        """
        if not self.public_key:
            raise ValueError(
                "Cannot encrypt when no public key is supplied")

        # Get encryptor and return encrypted buffer
        encryptor = PKCS1_OAEP.new(self.public_key)
        return encryptor.encrypt(buffer)

    def decrypt(self, buffer: bytes) -> bytes:
        """
        This method decrypts the buffer using the private key
        Function throws ValueError when the private key isn't supplied
        """
        if not self.private_key:
            raise ValueError(
                "Cannot decrypt when no public key is supplied")

        # Get encryptor and return encrypted buffer
        decryptor = PKCS1_OAEP.new(self.private_key)
        return decryptor.decrypt(buffer)
