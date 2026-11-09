import json
from protocols.enums import ProtocolParseStatus
from protocols.enums import HttpOneParseStatus
from dtos.request import HttpOneRequest
from dtos.connection import Connection
from dtos.response import Response

def is_valid_json(data: str) -> bool:
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def parse_http_11(connection: Connection) -> HttpOneRequest | ProtocolParseStatus | HttpOneParseStatus:
    buffer = connection.get_buffer()
    data = buffer.decode('utf-8', errors='replace')

    header_end = data.find('\r\n\r\n')

    if header_end == -1:
        return ProtocolParseStatus.NEED_MORE_DATA

    request_line_end_index = data.find('\r\n')

    request_line = data[:request_line_end_index]

    request_line_items = request_line.split(' ')
    method = request_line_items[0]
    path= request_line_items[1]

    header_data_end_index = data.find('\r\n\r\n')
    if header_data_end_index == -1:
        return ProtocolParseStatus.NEED_MORE_DATA

    header_data = data[request_line_end_index+2:header_data_end_index]
    header_lines = header_data.split('\r\n')

    headers = {}
    for header_line in header_lines:
        colon = header_line.find(':')
        key: str = header_line[:colon].strip().lower()
        value: str = header_line[colon+1:].strip()
        headers[key] = value

    if 'content-length' not in headers:
        return HttpOneParseStatus.MISSING_CONTENT_LENGTH

    if 'content-type' not in headers:
        return HttpOneParseStatus.MISSING_CONTENT_TYPE

    if headers['content-type'] != 'application/json':
        return HttpOneParseStatus.UNSUPPORTED_CONTENT_TYPE

    content_length = headers["content-length"]
    if not content_length.isdigit():
        return HttpOneParseStatus.INVALID_CONTENT_LENGTH

    content_length = int(content_length)
    if content_length < 0:
        return HttpOneParseStatus.INVALID_CONTENT_LENGTH

    body_start_index = header_data_end_index + 4
    body_end_index = body_start_index + content_length

    body = data[body_start_index:body_end_index]
    if len(body) < content_length:
        return ProtocolParseStatus.NEED_MORE_DATA

    if not is_valid_json(body):
        return HttpOneParseStatus.INVALID_BODY

    parsed_body = json.loads(body)

    return HttpOneRequest(
        method,
        path,
        headers,
        parsed_body
    )

def build_response(response: Response):
    response = (
        f"HTTP/1.1 {response.get_status()}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(response.get_body().encode('utf-8'))}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{response.get_body()}"
    )

    return response.encode('utf-8')