import socket
import time
import select
import requests
import os
import re
import threading
import string
import random

server_address = ('141.144.235.239', 8090)

# Cryptography

from Crypto.Cipher import AES

# Custom modules
from keypair import KeyPair

local_key_pair = KeyPair()
local_key_pair.add_keypair_from_files()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

test = "Hello world"

server_socket.connect(server_address)

server_socket.send(bytes(f"REGISTER,{local_key_pair.public_key_string}", encoding="UTF-8"))

response = server_socket.recv(4096)
if response == b"OK\n":
    print("Klient byl zaregistrován!")
else:
    print("Klienta nebylo možné zaregistrovat")
    exit(1)

print(f"Klíč klienta \n{local_key_pair.public_key_string}")

print("")
print("Napiš 'r' pro příjem, napiš 's' pro připojení")
role = "receiver"
if input() == "s":
    print("Vlož klíč od příjemce")
    receiverKey = input()
    role = "sender"
    server_socket.send(bytes(f"CONNECT,{ip},{local_key_pair.public_key_string},{receiverKey}", encoding="UTF-8"))
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

    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


    print("Připojování")
    got_responded = False
    responded = False
    for _ in range(5):
        hello_msg = "Hello " + generate_random_string(4) + "\n"
        p2p_socket.sendto(bytes(hello_msg, encoding="UTF-8"), dstIP)
        for _ in range(2):
            r, w, e = select.select([p2p_socket], [], [], 1)
            if len(r) != 0:
                responses = p2p_socket.recv(4096).decode("utf-8").splitlines()
                for response in responses:
                    if not response.startswith("Hello"):
                        continue

                    if response == hello_msg[:-1]:
                        got_responded = True
                    else:
                        p2p_socket.sendto(bytes(response + "\n", encoding="UTF-8"), dstIP)
                        responded = True

    time.sleep(0.2)
    if not responded and not got_responded:
        print("Nebylo možné navázat spojení")
    

    if role == "sender":
        remote_keypair = KeyPair()
        remote_keypair.add_keypair_custom(receiverKey, None)
        

        encryption_key = generate_random_string(32)
        p2p_socket.sendto(remote_keypair.encrypt(encryption_key.encode("utf-8")), dstIP)
    else:
        encryption_key = local_key_pair.decrypt(p2p_socket.recv(4096)).decode("UTF-8")

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
    stdscr.keypad(True) # enable keyboard use

    lastMessageLine = 1

    messageCharIndex = 0
    message = ""

    stop_threads = False
    
    def message_handle_thread():
        while True:
            r, w, e = select.select([p2p_socket], [], [], 2)

            global stop_threads
            if stop_threads:
                return

            if len(r) == 0: continue

            global stdscr
            global lastMessageLine
            global messageCharIndex

            bytemsg = p2p_socket.recv(4096)
            ciphertext = bytemsg[:-16]
            nonce = bytemsg[len(bytemsg)-16:]
            cipher = AES.new(encryption_key.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
            msg = cipher.decrypt(ciphertext)

            stdscr.addstr(lastMessageLine, 2, f"{dstIP[0]}: {msg.decode('utf-8')}")
            stdscr.move(maxY-2, 10 + messageCharIndex)
            stdscr.refresh()
            lastMessageLine += 1

    threading.Thread(target=message_handle_thread).start()

    while True:
        char = stdscr.getkey()
        curses.flushinp()

        if char in ['\x03']:
            # Exit on CTRL + C
            curses.echo()
            curses.nocbreak()
            stdscr.keypad(False)

            exit()
        elif char == '\n':
            stdscr.move(maxY-2, 10)
            stdscr.addstr(maxY-2, 10 , " "*(maxX - 11))

            stdscr.addstr(lastMessageLine, 2, f"{ip}: {message}")

            # Send message
            cipher = AES.new(encryption_key.encode("utf-8"), AES.MODE_EAX)
            nonce = cipher.nonce

            ciphertext, tag = cipher.encrypt_and_digest(message.encode("utf-8"))

            p2p_socket.sendto(ciphertext+nonce, dstIP)

            lastMessageLine += 1
            messageCharIndex = 0
            message = ""

            stdscr.move(maxY-2, 10)

        elif char in ['\x08', "KEY_BACKSPACE", "\b"]: # Backspace
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