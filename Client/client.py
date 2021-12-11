import socket
import time
import select
import json
import requests

port = 3000

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

sock.bind(("", port))

test = "Hello world"

while True:
    request = requests.get('http://192.168.1.33:8080')
    request.json()
    time.sleep(0.5)

while True:
    sock.sendto(bytes(test, encoding="UTF-8"), ("192.168.1.13", 2000))
    print("Sending")
    r, w, e = select.select([sock], [], [], 1)
    for s in r:
        if s == sock:
            data = sock.recv(4096)
            print(data)
    time.sleep(1)