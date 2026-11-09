class Request:
    def __init__(self):
        pass

class HttpOneRequest(Request):
    def __init__(self, method, path, headers, body):
        super().__init__()
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    def get_method(self):
        return self.method

    def get_headers(self):
        return self.headers

    def get_body(self):
        return self.body