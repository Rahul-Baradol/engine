from custom_types.value import Value

class MemoryStore:
    def __init__(self):
        self.store = dict[str, Value]()

    def get(self, key) -> Value:
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