import json
import os
import socket
import uuid
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
PORT = int(os.getenv("SERVER_BIND_PORT", 8080))


def unique_key(prefix="key"):
    """Keys are namespaced per call so tests don't collide on a long-running server."""
    return f"{prefix}:{uuid.uuid4().hex}"


def build_request(payload: dict) -> bytes:
    body = json.dumps(payload).encode()
    head = (
        "POST / HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()
    return head + body


def parse_response(raw: bytes):
    head, _, body = raw.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode()
    status = int(status_line.split(" ")[1])
    return status, body.decode()


def send(payload: dict, timeout=5):
    """Send one command over a fresh connection; returns (status, body)."""
    with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
        sock.sendall(build_request(payload))

        chunks = []
        while chunk := sock.recv(4096):
            chunks.append(chunk)

    return parse_response(b"".join(chunks))


def set_key(key, value, expire_after_seconds=None):
    payload = {"command": "SET", "key": key, "value": value}
    if expire_after_seconds is not None:
        payload["expire_after_seconds"] = expire_after_seconds
    return send(payload)


def get_key(key):
    return send({"command": "GET", "key": key})


def delete_key(key):
    return send({"command": "DELETE", "key": key})
