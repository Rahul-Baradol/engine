from core.enums import LogType
from core.logger import server_log
from dtos.request import HttpOneRequest
from dtos.request import Request
from dtos.response import Response
import time
from core.event_loop import EventLoop
from storage.memory_store import MemoryStore
from custom_types.value import Value

mem_store = MemoryStore()

def is_command(request: Request):
    match request:
        case HttpOneRequest():
            method = request.get_method()
            body = request.get_body()

            if method == "POST" and "command" in body:
                return True

        case _:
            return False

def expire_key(key, expire_time):
    now = time.monotonic()
    current_value: Value = mem_store.get(key)

    if current_value.get_gen_time() <= expire_time:
        mem_store.delete(key)
        server_log(LogType.INFO, f"EXPIRED {key} at {now}")
    else:
        server_log(LogType.INFO, f"EXPIRE triggered for {key} at {now}; ignoring bcuz generation times don't match")

def process_command(request: Request, loop: EventLoop) -> Response:
    match request:
        case HttpOneRequest():
            body = request.get_body()

            response = None
            if body["command"] == "GET":
                now = time.monotonic()
                server_log(LogType.INFO, f"GET \"{body['key']}\" at {now}")

                value = mem_store.get(body["key"])

                if not isinstance(value, Value):
                    response = Response(value, 404)
                else:
                    response = Response(value.get_value(), 200)
            elif body["command"] == "SET":
                now = time.monotonic()
                server_log(LogType.INFO, f"SET \"{body['key']} = {body['value']}\" at {now}")

                new_value = Value(body["value"])
                mem_store.set(body["key"], new_value)

                response = Response('ok', 200)
            elif body["command"] == "DELETE":
                now = time.monotonic()
                server_log(LogType.INFO, f"DELETE \"{body['key']}\" at {now}")

                mem_store.delete(body["key"])
                response = Response('ok', 200)
            elif body["command"] == "EXPIRE":   
                expire_time = time.monotonic()
                loop.call_later(body["seconds_after"], lambda: expire_key(body["key"], expire_time))
                response = Response('ok', 200)

            return response

        case _:
            return Response("couldn't process command: unknown child of Request class", 500)