import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from client import unique_key, set_key, get_key, delete_key

TOTAL = 1000
WORKERS = 200


def report(name, results, elapsed):
    successful = sum(results)
    print(f"\n[{name}]")
    print(f"Total requests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Throughput: {successful / elapsed:.2f} requests/sec")


def run(name, fn, n=TOTAL):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = list(executor.map(fn, range(n)))
    report(name, results, time.perf_counter() - start)
    return results


@pytest.mark.stress
def test_1000_sets_and_gets():
    prefix = unique_key("stress")

    def set_one(i):
        try:
            return set_key(f"{prefix}:{i}", f"value-{i}") == (200, "ok")
        except Exception:
            return False

    def get_one(i):
        try:
            return get_key(f"{prefix}:{i}") == (200, f"value-{i}")
        except Exception:
            return False

    assert all(run("SET", set_one))
    assert all(run("GET", get_one))


@pytest.mark.stress
def test_1000_full_lifecycles():
    prefix = unique_key("lifecycle")

    def lifecycle(i):
        key = f"{prefix}:{i}"
        try:
            return (
                set_key(key, str(i)) == (200, "ok")
                and get_key(key) == (200, str(i))
                and delete_key(key) == (200, "ok")
                and get_key(key) == (200, "<none>")
            )
        except Exception:
            return False

    assert all(run("SET/GET/DELETE/GET", lifecycle))


@pytest.mark.stress
def test_1000_expiring_keys():
    prefix = unique_key("stress-exp")

    def set_one(i):
        try:
            return set_key(f"{prefix}:{i}", "temp", expire_after_seconds=1) == (200, "ok")
        except Exception:
            return False

    def expired(i):
        try:
            return get_key(f"{prefix}:{i}") == (200, "<none>")
        except Exception:
            return False

    assert all(run("SET with expiry", set_one))
    time.sleep(2)
    assert all(run("GET after expiry", expired))
