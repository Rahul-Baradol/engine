class Response:
    def __init__(self, body: str = '', status: int = 200, headers: dict = None):
        self.body = body
        self.status = status
        self.headers = headers if headers is not None else {}

    def get_status(self):
        return self.status

    def get_body(self):
        return self.body

    def get_headers(self):
        return self.headers