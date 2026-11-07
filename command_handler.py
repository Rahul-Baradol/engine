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

def process_command(request: Request) -> Response:
    body = request.get_body()

    response = None
    if body["command"] == "GET":
        value = mem_store.get(body["key"])
        response = Response(value, 200)
    elif body["command"] == "SET":
        mem_store.set(body["key"], body["value"])
        response = Response('ok', 200)

    return response