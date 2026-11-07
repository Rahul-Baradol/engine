from wsgiref import headers
from protocol import Response
from command_handler import process_command
from command_handler import is_command
from protocol import Request

def handle_connection(client_socket, loop):
    data = client_socket.recv(4096)
    
    request = Request(data)

    if not is_command(request):
        response = Response("couldn't process request", 500)
        client_socket.sendall(response.build())
    else:
        response: Response = process_command(request)
        client_socket.sendall(response.build())

    client_socket.close()
    loop.unregister_socket(client_socket)