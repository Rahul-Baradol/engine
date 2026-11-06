import os
import socket
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

HOST = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
PORT = int(os.getenv("SERVER_BIND_PORT", 8080))

def make_request(client_id):
    try:
        with socket.create_connection(
            (HOST, PORT), timeout=5
        ) as sock:
            sock.sendall(f"Client {client_id}".encode())

            while sock.recv(1024):
                pass

            return True

    except Exception as e:
        print(f"Client {client_id} failed: {e}")
        return False


def test_100_concurrent_connections():
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(make_request, range(100)))

    assert all(results)