class Request:
    def __init__(self, data):
        self.data = data
        self.method = None
        self.headers = None
        self.body = None

    def get_data(self):
        return self.data

    def get_method(self):
        return self.method

    def get_headers(self):
        return self.headers

    def get_body(self):
        return self.body

    def set_method(self, method):
        self.method = method

    def set_headers(self, headers):
        self.headers = headers

    def set_body(self, body):
        self.body = body