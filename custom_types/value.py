import time

class Value:
    def __init__(self, value: str):
        self.value = value
        self.gen_time = time.monotonic()

    def __str__(self):
        return self.value

    def get_gen_time(self):
        return self.gen_time

    def get_value(self):
        return self.value