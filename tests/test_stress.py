import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from client import KeepAliveClient, unique_key, set_key, get_key, delete_key

TOTAL = 1000
WORKERS = 200

# "close": every request opens a fresh connection with `Connection: close`.
# "keep-alive": each worker thread reuses one persistent connection.
MODES = ["close", "keep-alive"]

def report(name, results, elapsed):
    successful = sum(results)
    print(f"\n[{name}]")
    print(f"Total requests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Throughput: {successful / elapsed:.2f} requests/sec")

def run(name, mode, fn, n=TOTAL):
    """Run fn(i, client) for i in range(n); client is None in "close" mode."""
    local = threading.local()
    clients = []
    lock = threading.Lock()

    def client_for_thread():
        if mode == "close":
            return None
        if not hasattr(local, "client"):
            local.client = KeepAliveClient()
            with lock:
                clients.append(local.client)
        return local.client

    def task(i):
        try:
            return fn(i, client_for_thread())
        except Exception:
            # A broken keep-alive connection shouldn't poison later requests on this thread.
            if hasattr(local, "client"):
                local.client.close()
                del local.client
            return False

    start = time.perf_counter()
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            results = list(executor.map(task, range(n)))
    finally:
        for client in clients:
            client.close()

    report(f"{name} [{mode}]", results, time.perf_counter() - start)
    return results

@pytest.mark.stress
@pytest.mark.parametrize("mode", MODES)
def test_1000_sets_and_gets(mode):
    prefix = unique_key("stress")

    def set_one(i, client):
        return set_key(f"{prefix}:{i}", f"value-{i}", client=client) == (200, "ok")

    def get_one(i, client):
        return get_key(f"{prefix}:{i}", client=client) == (200, f"value-{i}")

    assert all(run("SET", mode, set_one))
    assert all(run("GET", mode, get_one))

@pytest.mark.stress
@pytest.mark.parametrize("mode", MODES)
def test_1000_full_lifecycles(mode):
    prefix = unique_key("lifecycle")

    def lifecycle(i, client):
        key = f"{prefix}:{i}"
        return (
            set_key(key, str(i), client=client) == (200, "ok")
            and get_key(key, client=client) == (200, str(i))
            and delete_key(key, client=client) == (200, "ok")
            and get_key(key, client=client) == (200, "<none>")
        )

    assert all(run("SET/GET/DELETE/GET", mode, lifecycle))

@pytest.mark.stress
@pytest.mark.parametrize("mode", MODES)
def test_1000_expiring_keys(mode):
    prefix = unique_key("stress-exp")

    def set_one(i, client):
        return set_key(f"{prefix}:{i}", "temp", expire_after_seconds=1, client=client) == (200, "ok")

    def expired(i, client):
        return get_key(f"{prefix}:{i}", client=client) == (200, "<none>")

    assert all(run("SET with expiry", mode, set_one))
    time.sleep(4)
    assert all(run("GET after expiry", mode, expired))
