class Response:
    def __init__(self, body: str = '', status: int = 200):
        self.body = body
        self.status = status

    def get_status(self):
        return self.status

    def get_body(self):
        return self.body