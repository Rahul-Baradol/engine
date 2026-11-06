import os
import socket
import time
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
            sock.sendall(b"Stress test")

            while sock.recv(1024):
                pass

        return True

    except Exception as e:
        return False

def test_1000_connections():
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=200) as executor:
        results = list(executor.map(make_request, range(1000)))

    elapsed = time.perf_counter() - start

    successful = sum(results)
    failed = len(results) - successful

    print(f"Total requests: 1000")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Throughput: {successful / elapsed:.2f} connections/sec")

    assert failed == 0