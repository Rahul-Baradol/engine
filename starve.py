import socket
import time
import json

sock = socket.create_connection(("localhost", 8080))

sock.sendall(b"POST / HTTP/1.1\r\n")
time.sleep(5)

sock.sendall(
    b"Host: localhost\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 35\r\n"
)
time.sleep(5)

sock.sendall(b"\r\n")
time.sleep(5)

body = json.dumps({
    "command": "GET",
    "key": "bounce"
}).encode()

sock.sendall(body)

# Receive response
response = bytearray()

while True:
    data = sock.recv(4096)

    if not data:
        break

    response.extend(data)

print(response.decode())

sock.close()