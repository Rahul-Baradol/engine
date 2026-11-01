import heapq
import time 
import selectors
from collections import deque

class EventLoop:
    def __init__(self):
        self.tasks = deque()
        self.timers = []
        self.selector = selectors.DefaultSelector()
        self.running = False

    def enqueue(self, callback):
        self.tasks.append(callback)

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
                self.enqueue(
                    lambda cb = callback: cb(key.fileobj)
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