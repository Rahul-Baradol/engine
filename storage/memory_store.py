class MemoryStore:
    def __init__(self):
        self.store = dict()

    def get(self, key):
        if key not in self.store:
            return '<none>'
        return self.store[key]

    def set(self, key, value):
        self.store[key] = value

    def delete(self, key):
        if key in self.store:
            del self.store[key]

    def clear_store(self):
        self.store = dict()