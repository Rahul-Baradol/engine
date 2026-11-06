from contants import SERVER_BIND_PORT
from contants import SERVER_BIND_ADDRESS
from event_loop import EventLoop
import socket

def build_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_BIND_ADDRESS, SERVER_BIND_PORT))
    server.setblocking(False)
    server.listen()
    return server

def setup_loop_for_server(loop: EventLoop, server_socket: socket.socket):
    def handle_connection(client_socket):
        data = client_socket.recv(1024)
        print(data.decode())
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