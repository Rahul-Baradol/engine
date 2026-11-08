from dtos.response import Response
from dtos.request import Request
import json
import h11
    
def parse_request(request: Request):
    data = request.get_data()

    conn = h11.Connection(h11.SERVER)
    conn.receive_data(data)

    headers = {}
    method = ''
    body = ''

    while True:
        event = conn.next_event()

        if event is h11.NEED_DATA:
            break

        if isinstance(event, h11.Request):
            method = event.method.decode()
            headers = {k.decode(): v.decode() for k, v in event.headers}

        elif isinstance(event, h11.Data):
            body += event.data.decode()

        elif isinstance(event, h11.EndOfMessage) or isinstance(event, h11.ConnectionClosed):
            break

    try:
        parsed_body = json.loads(body)
        return method, headers, parsed_body
    except json.JSONDecodeError:
        return method, headers, {}

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