import json
import h11

class Request:
    def __init__(self, data):
        self.data = data
        method, headers, body = self._parse()

        self.method = method
        self.headers = headers
        self.body = body
    
    def _parse(self):
        conn = h11.Connection(h11.SERVER)
        conn.receive_data(self.data)

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

            elif isinstance(event, h11.EndOfMessage):
                break

        parsed_body = json.loads(body)
        return method, headers, parsed_body

    def get_method(self):
        return self.method

    def get_headers(self):
        return self.headers

    def get_body(self):
        return self.body

class Response:
    def __init__(self, body: str = '', status: int = 200):
        self.body = body
        self.status = status

    def build(self):
        response = (
            f"HTTP/1.1 {self.status}\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            f"Content-Length: {len(self.body.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{self.body}"
        )

        return response.encode('utf-8')