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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

print("")
print("Napiš 'r' pro příjem, napiš 's' pro připojení")
if input() == "s":
    print("Vlož klíč od příjemce")
    receiverKey = input()
    server_socket.send(bytes(f"CONNECT,{ip},{public_key_string},{receiverKey}", encoding="UTF-8"))
else:
    print("Čekáme na příjem")


response = server_socket.recv(4096)
response = response.decode("UTF-8")
if response.startswith("NO"):
    print("Nebylo možné se připojit")
    exit(1)
else:
    data = response.split(",")
    print(f"{data} - Lokální port: {int(data[3])}, Vzdálená ip/port: {(str(data[1]), int(data[2]))}")
    p2p_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    p2p_socket.bind(("", int(data[3])))

    dstIP = (str(data[1]), int(data[2]))

    print("Připojování")
    while True:
        p2p_socket.sendto(bytes("Hello", encoding="UTF-8"), dstIP)
        r, w, e = select.select([p2p_socket], [], [], 1)
        if len(r) != 0:
            data = p2p_socket.recv(4096)
            if data == b"Hello":
                break
    
    print("Připojeno!")
        

    while True:
        p2p_socket.sendto(bytes(test, encoding="UTF-8"), dstIP)
        r, w, e = select.select([p2p_socket], [], [], 1)
        for s in r:
            if s == p2p_socket:
                data = p2p_socket.recv(4096)
                print(data)
        time.sleep(1)