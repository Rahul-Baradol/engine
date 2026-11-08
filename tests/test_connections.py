import socket
import time

from client import HOST, PORT, build_request, unique_key, set_key, get_key, delete_key


def test_server_accepts_connection():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        assert sock is not None


def test_server_closes_connection_after_response():
    key = unique_key()
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(build_request({"command": "GET", "key": key}))

        data = b""
        while chunk := sock.recv(4096):
            data += chunk

        # recv returned b"" -> server closed the connection after replying
        assert data.startswith(b"HTTP/1.1 200")


def test_set_then_get():
    key = unique_key()

    assert set_key(key, "hello") == (200, "ok")
    assert get_key(key) == (200, "hello")


def test_get_missing_key():
    assert get_key(unique_key()) == (200, "<none>")


def test_set_overwrites_value():
    key = unique_key()

    set_key(key, "first")
    set_key(key, "second")

    assert get_key(key) == (200, "second")


def test_delete():
    key = unique_key()
    set_key(key, "to-be-deleted")

    assert delete_key(key) == (200, "ok")
    assert get_key(key) == (200, "<none>")


def test_delete_missing_key():
    assert delete_key(unique_key()) == (200, "ok")


def test_set_with_expiry():
    key = unique_key()

    assert set_key(key, "temporary", expire_after_seconds=0.5) == (200, "ok")
    assert get_key(key) == (200, "temporary")

    time.sleep(1)

    assert get_key(key) == (200, "<none>")
