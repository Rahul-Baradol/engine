from core.event_loop import EventLoop
from core.protocol import parse_request
from handlers.command import process_command
from handlers.command import is_command
from core.protocol import build_response
from dtos.response import Response
from dtos.connection import Connection
from core.protocol import Request

def handle_connection(connection: Connection, loop: EventLoop):
    connection_id = connection.get_connection_id()
    client_socket = connection.get_client_socket()

    print(f"Handling connection {connection_id}")

    data = client_socket.recv(4096)
    
    request = Request(data)
    
    method, headers, body = parse_request(request)
    request.set_method(method)
    request.set_headers(headers)
    request.set_body(body)

    if not is_command(request):
        response = Response("couldn't process request", 500)
        client_socket.sendall(build_response(response))
    else:
        response: Response = process_command(request, loop)
        client_socket.sendall(build_response(response))

    print(f"Closing connection {connection_id}")
    client_socket.close()
    loop.unregister_socket(client_socket)