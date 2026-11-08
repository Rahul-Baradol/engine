import socket
import time

HOST = "127.0.0.1"
PORT = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.send(b"Chumma!")

print(f"Connected to {HOST}:{PORT}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    sock.close()