from uuid import uuid4

class Connection:
    def __init__(self, transport_layer_protocol, client_socket, client_address):
        self.transport_layer_protocol = transport_layer_protocol
        self.client_socket = client_socket
        self.client_address = client_address

        self.connection_id = uuid4()
        self.buffer = bytearray()
        
    def add_to_buffer(self, data):
        self.buffer.extend(data)
    
    def get_buffer(self):
        return self.buffer

    def get_connection_id(self):
        return self.connection_id

    def get_client_socket(self):
        return self.client_socket

    def get_client_address(self):
        return self.client_address