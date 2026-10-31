import heapq
from collections import deque
import time 

class EventLoop:
    def __init__(self):
        self.tasks = deque()
        self.timers = []

    def enqueue(self, callback):
        self.tasks.append(callback)

    def run(self):
        while self.tasks or self.timers:
            now = time.monotonic()
            while self.timers and self.timers[0][0] <= now:
                element = heapq.heappop(self.timers)
                self.tasks.append(element[1])

            if self.tasks:
                callback = self.tasks.popleft()
                callback()

    def call_later(self, delay, callback):
        next_execute_at = time.monotonic() + delay

        heapq.heappush(self.timers, 
            (next_execute_at, callback)
        )