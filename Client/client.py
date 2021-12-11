import socket
import time
import select
import json
import requests
import os
import re

server_address = ("172.20.201.136", 8090)

# Cryptography
from Crypto.PublicKey import RSA
from Crypto import Random


if not os.path.isdir("keys"):
    os.mkdir("keys")

if not os.path.isfile(os.path.join("keys","private_key")):
    print("Klíčový pár neexistuje, regenerujeme!")
    key = RSA.generate(2048)
    private_key = key
    public_key = key.publickey()
    
    file_out = open(os.path.join("keys","private_key"), "wb")
    file_out.write(private_key.exportKey())
    file_out.close()

    file_out = open(os.path.join("keys","public_key"), "wb")
    file_out.write(public_key.export_key())
    file_out.close()
else:
    public_key_file = open(os.path.join("keys","public_key"), "r")
    public_key = RSA.import_key(public_key_file.read())
    public_key_file.close()

    private_key_file = open(os.path.join("keys","private_key"), "r")
    private_key = RSA.import_key(private_key_file.read())
    private_key_file.close()

public_key_string = public_key.export_key().decode("utf-8").replace("\n", "")
public_key_string = re.sub("-+[A-Z ]+-+", "", public_key_string)

private_key_string = private_key.export_key().decode("utf-8").replace("\n", "")
private_key_string = re.sub("-+[A-Z ]+-+", "", private_key_string)

port = 25343



p2p_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

p2p_socket.bind(("", port))

test = "Hello world"

# Get public IP
request = requests.get('https://api.ipify.org?format=json')
ip = request.json()["ip"]

server_socket.connect(server_address)

server_socket.send(bytes(f"REGISTER,{public_key_string},{ip}", encoding="UTF-8"))

response = server_socket.recv(4096)
if response == b"OK\n":
    print("Klient byl zaregistrován!")
else:
    print("Klienta nebylo možné zaregistrovat")
    exit(1)

print(f"Klíč klienta \n{public_key_string}")

while True:
    pass

while True:
    p2p_socket.sendto(bytes(test, encoding="UTF-8"), ("31.222.4.120", 21600))
    print("Sending")
    r, w, e = select.select([p2p_socket], [], [], 1)
    for s in r:
        if s == p2p_socket:
            data = p2p_socket.recv(4096)
            print(data)
    time.sleep(1)