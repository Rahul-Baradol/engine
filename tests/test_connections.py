import socket
import time

import pytest

from client import (
    HOST, PORT, KeepAliveClient, build_request, read_full_response, read_response,
    server_closed, unique_key, set_key, get_key, delete_key,
)

def test_server_accepts_connection():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        assert sock is not None

# --- Connection: keep-alive ---------------------------------------------------

@pytest.mark.parametrize("connection", [None, "keep-alive", "Keep-Alive"])
def test_server_keeps_connection_open_after_response(connection):
    """No Connection header (HTTP/1.1 default) or keep-alive -> connection stays open."""
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(build_request({"command": "GET", "key": unique_key()}, connection=connection))

        assert read_response(sock) == (200, "<none>")
        assert not server_closed(sock), "Server closed a keep-alive connection"

def test_keep_alive_response_does_not_announce_close():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(build_request({"command": "GET", "key": unique_key()}, connection="keep-alive"))

        status, headers, _ = read_full_response(sock)
        assert status == 200
        assert headers.get("connection", "keep-alive").lower() != "close"

def test_multiple_requests_on_one_connection():
    key = unique_key()

    with KeepAliveClient() as client:
        assert set_key(key, "first", client=client) == (200, "ok")
        assert get_key(key, client=client) == (200, "first")
        assert set_key(key, "second", client=client) == (200, "ok")
        assert get_key(key, client=client) == (200, "second")
        assert delete_key(key, client=client) == (200, "ok")
        assert get_key(key, client=client) == (200, "<none>")

def test_many_requests_on_one_connection():
    prefix = unique_key("ka")

    with KeepAliveClient() as client:
        for i in range(100):
            assert set_key(f"{prefix}:{i}", str(i), client=client) == (200, "ok")
        for i in range(100):
            assert get_key(f"{prefix}:{i}", client=client) == (200, str(i))

def test_pipelined_requests_on_one_connection():
    """Two requests sent in a single write must get two responses, in order."""
    key = unique_key()

    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(
            build_request({"command": "SET", "key": key, "value": "v"}, connection="keep-alive")
            + build_request({"command": "GET", "key": key}, connection="keep-alive")
        )

        assert read_response(sock) == (200, "ok")
        assert read_response(sock) == (200, "v")

def test_expiry_on_keep_alive_connection():
    key = unique_key()

    with KeepAliveClient() as client:
        assert set_key(key, "temporary", expire_after_seconds=0.5, client=client) == (200, "ok")
        assert get_key(key, client=client) == (200, "temporary")

        time.sleep(1)

        assert get_key(key, client=client) == (200, "<none>")

# --- Connection: close --------------------------------------------------------

@pytest.mark.parametrize("connection", ["close", "Close", "CLOSE"])
def test_server_closes_connection_after_response(connection):
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(build_request({"command": "GET", "key": unique_key()}, connection=connection))

        assert read_response(sock) == (200, "<none>")
        assert server_closed(sock), "Server kept the connection open despite Connection: close"

def test_close_response_announces_close():
    with socket.create_connection((HOST, PORT), timeout=3) as sock:
        sock.sendall(build_request({"command": "GET", "key": unique_key()}, connection="close"))

        _, headers, _ = read_full_response(sock)
        assert headers.get("connection", "").lower() == "close"

def test_close_after_keep_alive_requests():
    """A connection used for keep-alive requests closes once a request asks for it."""
    key = unique_key()

    with KeepAliveClient() as client:
        assert set_key(key, "v", client=client) == (200, "ok")
        assert client.send({"command": "GET", "key": key}, connection="close") == (200, "v")
        assert server_closed(client.sock)

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
