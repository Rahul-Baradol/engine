from collections import deque

class EventLoop:
    def __init__(self):
        self.tasks = deque()

    def enqueue(self, callback):
        self.tasks.append(callback)

    def run(self):
        while len(self.tasks) > 0:
            callback = self.tasks.popleft()
            callback()