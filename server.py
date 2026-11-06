from memory_store import MemoryStore
from event_loop import EventLoop
import socket
from dotenv import load_dotenv
import os
import h11
import json

load_dotenv()

SERVER_BIND_ADDRESS = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
SERVER_BIND_PORT = int(os.getenv("SERVER_BIND_PORT", 8080))

mem_store = MemoryStore()

def build_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_BIND_ADDRESS, SERVER_BIND_PORT))
    server.setblocking(False)
    server.listen()
    return server

def parse_request(data):
    conn = h11.Connection(h11.SERVER)
    conn.receive_data(data)

    event = conn.next_event()

    method = ''
    body = ''

    while True:
        event = conn.next_event()

        if event is h11.NEED_DATA:
            break

        if isinstance(event, h11.Request):
            method = event.method.decode()

        elif isinstance(event, h11.Data):
            body += event.data.decode()

        elif isinstance(event, h11.EndOfMessage):
            break

    parsed_body = json.loads(body)
    return parsed_body

def send_response(client_socket, body: str, status="200 OK"):
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{body}"
    )

    client_socket.sendall(response.encode("utf-8"))

def setup_loop_for_server(loop: EventLoop, server_socket: socket.socket):
    def handle_connection(client_socket):
        data = client_socket.recv(4096)
        
        body = parse_request(data)

        if body["command"] == "GET":
            result = mem_store.get(body["key"])
            send_response(client_socket, result, 200)
        elif body["command"] == "SET":
            mem_store.set(body["key"], body["value"])
            send_response(client_socket, "ok", 200)

        client_socket.close()
        loop.unregister_socket(client_socket)

    def server_accept_callback(server_socket: socket.socket):
        client_socket, client_address = server_socket.accept()
        loop.register_socket(client_socket, handle_connection)

    loop.register_socket(server_socket, server_accept_callback)

if __name__ == "__main__":
    loop = EventLoop()
    server = build_server()

    setup_loop_for_server(loop, server)

    print(f"Starting server...")
    print(f"Binded to {SERVER_BIND_ADDRESS}:{SERVER_BIND_PORT}\n")
    loop.run()