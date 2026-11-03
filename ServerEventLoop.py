import heapq
import socket
import time 
import selectors
from collections import deque

class ServerEventLoop:
    def __init__(self, bind_address = '0.0.0.0', bind_port = 8080):
        self.handle_connection = self._handle_connection
        self.tasks = deque()
        self.timers = []
        self.selector = selectors.DefaultSelector()
        self.running = False
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.bind((bind_address, bind_port))
        server.listen()

        self.server = server
        self.register_socket(self.server, self._accept_connection)            

        print(f"Binded to {bind_address}:{bind_port}")
        print("Listening...")

    def _handle_connection(self, socket):
        data = socket.recv(1024)
        print(data.decode())
        socket.close()

        self.unregister_socket(socket)

    def enqueue(self, callback):
        self.tasks.append(callback)

    def _accept_connection(self, server_socket):
        try:
            client_socket, client_address = server_socket.accept()    
            self.register_socket(client_socket, self.handle_connection)
        except BlockingIOError:
            print("Bounce")
            return

    def run(self):
        self.running = True 

        while self.running:
            now = time.monotonic()

            while self.timers and (self.timers[0][0] <= now):
                current = heapq.heappop(self.timers)
                self.enqueue(current[1])

            if self.tasks:
                current_task = self.tasks.popleft()
                current_task()
                continue

            timeout = None

            if self.timers:
                timeout = max(
                    0, self.timers[0][0] - time.monotonic()
                )

            events = self.selector.select(timeout)

            for key, mask in events:
                callback = key.data
                fileobj = key.fileobj

                self.enqueue(
                    lambda cb = callback, sock = fileobj: cb(sock)
                )

    def stop(self):
        self.enqueue(
            lambda: setattr(self, "running", False)
        )

    def call_later(self, delay, callback):
        next_execute_at = time.monotonic() + delay

        heapq.heappush(self.timers, 
            (next_execute_at, callback)
        )

    def register_socket(self, socket, callback):
        socket.setblocking(False)

        self.selector.register(
            socket, selectors.EVENT_READ, callback
        )

    def unregister_socket(self, socket):
        self.selector.unregister(socket)

