from uuid import uuid4

class Connection:
    def __init__(self, client_socket, client_address):
        self.connection_id = uuid4()
        self.client_socket = client_socket
        self.client_address = client_address

    def get_connection_id(self):
        return self.connection_id

    def get_client_socket(self):
        return self.client_socket

    def get_client_address(self):
        return self.client_address