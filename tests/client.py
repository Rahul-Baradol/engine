import json
import os
import socket
import uuid
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
PORT = int(os.getenv("SERVER_BIND_PORT", 8080))

def unique_key(prefix="key"):
    return f"{prefix}:{uuid.uuid4().hex}"

def build_request(payload: dict, connection: str | None = "close") -> bytes:
    """Build a POST request. `connection` sets the Connection header; None omits it."""
    body = json.dumps(payload).encode()
    head = (
        "POST / HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
    )
    if connection is not None:
        head += f"Connection: {connection}\r\n"
    head += "\r\n"
    return head.encode() + body

def parse_response(raw: bytes):
    head, _, body = raw.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode()
    status = int(status_line.split(" ")[1])
    return status, body.decode()

def read_full_response(sock):
    """Read exactly one response; returns (status, headers, body) with lowercase header names."""
    response = b""

    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed before headers completed")
        response += chunk

    headers_end = response.index(b"\r\n\r\n")
    head = response[:headers_end].decode()
    body = response[headers_end + 4:]

    status_line, *header_lines = head.split("\r\n")
    status = int(status_line.split(" ")[1])

    headers = {}
    for line in header_lines:
        key, _, value = line.partition(":")
        headers[key.strip().lower()] = value.strip()

    if "content-length" not in headers:
        raise ValueError("Missing Content-Length")
    content_length = int(headers["content-length"])

    while len(body) < content_length:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed before response completed")
        body += chunk

    return status, headers, body[:content_length].decode()

def read_response(sock):
    status, _, body = read_full_response(sock)
    return status, body

def server_closed(sock, wait=1.0) -> bool:
    """True if the server closed the connection within `wait` seconds."""
    sock.settimeout(wait)
    try:
        return sock.recv(1) == b""
    except socket.timeout:
        return False
    except ConnectionResetError:
        return True

def send(payload: dict, timeout=5):
    """Send one command over a fresh connection with `Connection: close`; returns (status, body)."""
    with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(build_request(payload, connection="close"))

        return read_response(sock)

class KeepAliveClient:
    """One persistent connection reused for many requests."""

    def __init__(self, timeout=5):
        self.sock = socket.create_connection((HOST, PORT), timeout=timeout)
        self.sock.settimeout(timeout)

    def send(self, payload: dict, connection: str | None = "keep-alive"):
        self.sock.sendall(build_request(payload, connection=connection))
        return read_response(self.sock)

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

def _send(payload, client):
    return client.send(payload) if client is not None else send(payload)

def set_key(key, value, expire_after_seconds=None, client=None):
    payload = {"command": "SET", "key": key, "value": value}
    if expire_after_seconds is not None:
        payload["expire_after_seconds"] = expire_after_seconds
    return _send(payload, client)

def get_key(key, client=None):
    return _send({"command": "GET", "key": key}, client)

def delete_key(key, client=None):
    return _send({"command": "DELETE", "key": key}, client)
