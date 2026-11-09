from core.env import SERVER_BIND_PORT
from core.env import SERVER_BIND_ADDRESS
from core.enums import LogType
from core.logger import server_log
from protocols.enums import TransportLayerProtocol
from handlers.connection import handle_connection
from dtos.connection import Connection
from core.event_loop import EventLoop
import socket

def build_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_BIND_ADDRESS, SERVER_BIND_PORT))
    server.setblocking(False)
    server.listen()
    return server

def setup_loop_for_server(loop: EventLoop, server_socket: socket.socket):
    def server_accept_callback(server_socket: socket.socket):
        client_socket, client_address = server_socket.accept()

        server_log(LogType.INFO, f"accepted connection from {client_address}")
        connection = Connection(TransportLayerProtocol.TLS, client_socket, client_address)
        loop.register_socket(client_socket, lambda socket: handle_connection(connection, loop))

    server_log(LogType.INFO, "registering server socket to event loop")
    loop.register_socket(server_socket, server_accept_callback)

if __name__ == "__main__":
    loop = EventLoop()
    server = build_tcp_server()

    setup_loop_for_server(loop, server)

    server_log(LogType.INFO, f"Starting server...", force_log=True)
    server_log(LogType.INFO, f"Binded to {SERVER_BIND_ADDRESS}:{SERVER_BIND_PORT}\n", force_log=True)
    loop.run()