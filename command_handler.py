import time
from event_loop import EventLoop
from protocol import Response
from protocol import Request
from memory_store import MemoryStore

mem_store = MemoryStore()

def is_command(request: Request):
    method = request.get_method()
    body = request.get_body()

    if method == "POST" and "command" in body:
        return True
    return False

def expire_key(key):
    now = time.monotonic()
    mem_store.delete(key)
    print(f"EXPIRED {key} at {now}")

def process_command(request: Request, loop: EventLoop) -> Response:
    body = request.get_body()

    response = None
    if body["command"] == "GET":
        now = time.monotonic()
        print(f"GET \"{body['key']}\" at {now}")

        value = mem_store.get(body["key"])
        response = Response(value, 200)
    elif body["command"] == "SET":
        now = time.monotonic()
        print(f"SET \"{body['key']} = {body['value']}\" at {now}")
        mem_store.set(body["key"], body["value"])

        if "expire_after_seconds" in body:
            loop.call_later(body["expire_after_seconds"], lambda: expire_key(body["key"]))

        response = Response('ok', 200)
    elif body["command"] == "DELETE":
        now = time.monotonic()
        print(f"DELETE \"{body['key']}\" at {now}")

        mem_store.delete(body["key"])
        response = Response('ok', 200)

    return response