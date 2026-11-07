from connection_handler import handle_connection
from event_loop import EventLoop
import socket
from dotenv import load_dotenv
import os

load_dotenv()

SERVER_BIND_ADDRESS = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
SERVER_BIND_PORT = int(os.getenv("SERVER_BIND_PORT", 8080))

def build_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_BIND_ADDRESS, SERVER_BIND_PORT))
    server.setblocking(False)
    server.listen()
    return server

def setup_loop_for_server(loop: EventLoop, server_socket: socket.socket):
    def server_accept_callback(server_socket: socket.socket):
        client_socket, client_address = server_socket.accept()
        loop.register_socket(client_socket, lambda socket: handle_connection(socket, loop))

    loop.register_socket(server_socket, server_accept_callback)

if __name__ == "__main__":
    loop = EventLoop()
    server = build_server()

    setup_loop_for_server(loop, server)

    print(f"Starting server...")
    print(f"Binded to {SERVER_BIND_ADDRESS}:{SERVER_BIND_PORT}\n")
    loop.run()