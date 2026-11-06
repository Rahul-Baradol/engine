import os
import socket
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
PORT = int(os.getenv("SERVER_BIND_PORT", 8080))

def test_server_accepts_connection():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        assert sock is not None

def test_server_accepts_data():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(b"Hello server")

        # Your current server closes the connection after receiving data.
        response = sock.recv(1024)

        assert response == b""