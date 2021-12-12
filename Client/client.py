import socket
import time
import select
import json
import Crypto
import requests
import os
import sys
import re
import threading
import string
import random

server_address = ('172.25.52.202', 8090)

# Cryptography
from Crypto.PublicKey import RSA
from Crypto import Random

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES


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
role = "receiver"
if input() == "s":
    print("Vlož klíč od příjemce")
    receiverKey = input()
    role = "sender"
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
    

    if role == "sender":
        remote_key = RSA.import_key("-----BEGIN PUBLIC KEY-----\n"+receiverKey+"\n-----END PUBLIC KEY-----")

        def generate_random_string(length):
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

        encryptor = PKCS1_OAEP.new(remote_key)
        encryption_key = generate_random_string(32)
        p2p_socket.sendto(encryptor.encrypt(encryption_key.encode("utf-8")), dstIP)
    else:
        decryptor = PKCS1_OAEP.new(private_key)
        encryption_key = decryptor.decrypt(p2p_socket.recv(4096)).decode("UTF-8")

    print(encryption_key)
    time.sleep(2)
    
    print("Připojeno!")

    import curses

    stdscr = curses.initscr()

    maxY, maxX = stdscr.getmaxyx()

    # Draw border
    stdscr.border('|', '|', '-', '-', '+', '+', '+', '+')

    # Draw message field
    stdscr.addstr(maxY-3, 0, f"+{'-'*(maxX-2)}+")
    stdscr.addstr(maxY-2, 2, "Zpráva:")

    # Set cursor to the message field
    stdscr.move(maxY-2, 10)

    curses.noecho() # disable the keypress echo to prevent double input
    curses.cbreak() # disable line buffers to run the keypress immediately
    curses.curs_set(1)
    stdscr.keypad(1) # enable keyboard use

    lastMessageLine = 1

    messageCharIndex = 0
    message = ""
    
    def message_handle_thread():
        while True:
            r, w, e = select.select([p2p_socket], [], [])
            global stdscr
            global lastMessageLine
            global messageCharIndex

            bytemsg = p2p_socket.recv(4096)
            ciphertext = bytemsg[:-16]
            nonce = bytemsg[len(bytemsg)-16:]
            cipher = AES.new(encryption_key.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
            msg = cipher.decrypt(ciphertext)

            stdscr.addstr(lastMessageLine, 2, f"##: {msg.decode('utf-8')}")
            stdscr.move(maxY-2, 10 + messageCharIndex)
            stdscr.refresh()
            lastMessageLine += 1

    threading.Thread(target=message_handle_thread).start()

    while True:
        char = stdscr.get_wch()
        curses.flushinp()

        if char == '\x03':
            # Exit on CTRL + C
            exit()
        elif char == '\n':
            stdscr.move(maxY-2, 10)
            stdscr.addstr(maxY-2, 10 , " "*(maxX - 11))

            stdscr.addstr(lastMessageLine, 2, f"Já: {message}")

            # Send message
            cipher = AES.new(encryption_key.encode("utf-8"), AES.MODE_EAX)
            nonce = cipher.nonce

            ciphertext, tag = cipher.encrypt_and_digest(message.encode("utf-8"))

            p2p_socket.sendto(ciphertext+nonce, dstIP)

            lastMessageLine += 1
            messageCharIndex = 0
            message = ""

            stdscr.move(maxY-2, 10)

        elif char == '\x08': # Backspace
            message = message[:-1]
            messageCharIndex -= 1
            if messageCharIndex < 0:
                messageCharIndex = 0

            stdscr.addstr(maxY-2, 10 + messageCharIndex, " ")
            stdscr.move(maxY - 2, 10 + messageCharIndex)

        else:
            message += char
            stdscr.addstr(maxY-2, 10 + messageCharIndex, char)
            messageCharIndex += 1
            stdscr.refresh()