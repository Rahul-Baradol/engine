from core.enums import LogType
from core.logger import server_log
from handlers.command import process_command
from handlers.command import is_command
from dtos.request import Request
from protocols.enums import HttpOneParseStatus
from dtos.request import HttpOneRequest
from protocols.http11 import parse_http_11
from protocols.enums import ProtocolParseStatus
from protocols.http11 import build_response
from protocols.enums import ApplicationProtocol
from protocols.detector import detect_application_protocol
from core.event_loop import EventLoop

from dtos.response import Response
from dtos.connection import Connection

def did_receive_data_from_socket(connection: Connection) -> bool:
    connection_id = connection.get_connection_id()
    client_socket = connection.get_client_socket()

    try:
        data = client_socket.recv(4096)

        if data == b"":
            return False

        server_log(LogType.INFO, f"extending buffer of connection {connection_id}")
        connection.add_to_buffer(data)
        return True
    except ConnectionResetError:
        server_log(LogType.INFO, f"client unexpectedly closed the connection {connection_id}")
        return False

def is_keep_alive(request: Request) -> bool:
    match request:
        case HttpOneRequest():
            headers = request.get_headers()
            if "connection" not in headers:
                return True
            
            value = headers['connection']
            return value == 'keep-alive'

        case _:
            server_log(LogType.ERROR, "couldn't process request: unknown child of Request class")
            return False

def handle_connection(connection: Connection, loop: EventLoop):
    connection_id = connection.get_connection_id()
    client_socket = connection.get_client_socket()

    server_log(LogType.INFO, f"handling connection {connection_id}")

    if not did_receive_data_from_socket(connection):
        server_log(LogType.INFO, f"connection {connection_id} closed by client")

        server_log(LogType.INFO, f"unregistering socket of connection {connection_id} from event loop")
        loop.unregister_socket(client_socket)
        return

    protocol = detect_application_protocol(connection)
    if protocol == ProtocolParseStatus.NEED_MORE_DATA:
        server_log(LogType.INFO, f"connection {connection_id} needs more data")
        return
    
    if protocol == ProtocolParseStatus.UNKNOWN or protocol == ProtocolParseStatus.UNSUPPORTED:
        type = "unsupported" if protocol == ProtocolParseStatus.UNSUPPORTED else "unknown"
        response = Response(f"{type} protocol", 400)
        client_socket.sendall(build_response(response))

        server_log(LogType.INFO, f"{protocol} protocol for connection {connection_id}")
        server_log(LogType.INFO, f"closing connection {connection_id}")
        client_socket.close()

        server_log(LogType.INFO, f"unregistering socket of connection {connection_id} from event loop")
        loop.unregister_socket(client_socket)
        return

    request: Request = None
    if protocol == ApplicationProtocol.HTTP11:
        result: HttpOneRequest | ProtocolParseStatus | HttpOneParseStatus = parse_http_11(connection)
        if result == ProtocolParseStatus.NEED_MORE_DATA:
            server_log(LogType.INFO, f"connection {connection_id} needs more data")
            return

        if (result == HttpOneParseStatus.MISSING_CONTENT_TYPE
            or result == HttpOneParseStatus.MISSING_CONTENT_LENGTH
            or result == HttpOneParseStatus.INVALID_CONTENT_TYPE
            or result == HttpOneParseStatus.INVALID_CONTENT_LENGTH 
            or result == HttpOneParseStatus.UNSUPPORTED_CONTENT_TYPE):
            response = Response(result, 400)
            client_socket.sendall(build_response(response))

            server_log(LogType.INFO, f"unable to frame incoming request from connection {connection_id}")
            server_log(LogType.INFO, f"closing connection {connection_id}")    
            client_socket.close()

            server_log(LogType.INFO, f"unregistering socket of connection {connection_id} from event loop")
            loop.unregister_socket(client_socket)
            return

        request = result

    if not is_command(request):
        response = Response("couldn't process request", 400)

        server_log(LogType.INFO, f"unable to process request from connection {connection_id}")
        client_socket.sendall(build_response(response))
    else:
        response: Response = process_command(request, loop)

        server_log(LogType.INFO, f"responding to request from connection {connection_id}")
        client_socket.sendall(build_response(response))

    if not is_keep_alive(request):
        server_log(LogType.INFO, f"closing the connection {connection_id}")
        client_socket.close()

        server_log(LogType.INFO, f"unregistering the socket of connection {connection_id} from event loop")
        loop.unregister_socket(client_socket)