from protocols.enums import ProtocolParseStatus
from protocols.enums import ApplicationProtocol
from dtos.connection import Connection
import re

MAX_BUFFER_LIMIT = 8192

HTTP2_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"

SSH_PREFIX = b"SSH-"

HTTP11_METHODS = {
    b"GET",
    b"POST",
    b"PUT",
    b"DELETE",
    b"HEAD",
    b"OPTIONS",
    b"PATCH",
    b"TRACE",
    b"CONNECT",
}

HTTP11_REQUEST_LINE = re.compile(
    rb"^([A-Z]+) ([^\r\n ]+) HTTP/1\.[01]\r\n$"
)

def detect_application_protocol(connection: Connection) -> ApplicationProtocol | ProtocolParseStatus:
    buffer = connection.get_buffer()

    if not buffer:
        return ProtocolParseStatus.NEED_MORE_DATA

    if HTTP2_PREFACE.startswith(buffer):
        if buffer.startswith(HTTP2_PREFACE):
            return ApplicationProtocol.HTTP2

        return ProtocolParseStatus.UNKNOWN

    if SSH_PREFIX.startswith(buffer):
        if buffer.startswith(SSH_PREFIX):
            return ProtocolParseStatus.UNSUPPORTED

        return ProtocolParseStatus.NEED_MORE_DATA

    first_line_end = buffer.find(b"\r\n")

    if first_line_end == -1:
        if len(buffer) > MAX_BUFFER_LIMIT:
            return ProtocolParseStatus.UNKNOWN
        
        return ProtocolParseStatus.NEED_MORE_DATA

    request_line = buffer[:first_line_end + 2]

    match = HTTP11_REQUEST_LINE.match(request_line)

    if match:
        method = match.group(1)

        if method in HTTP11_METHODS:
            return ApplicationProtocol.HTTP11
        
    return ProtocolParseStatus.UNKNOWN
