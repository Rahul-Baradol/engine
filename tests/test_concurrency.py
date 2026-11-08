import time
from concurrent.futures import ThreadPoolExecutor

from client import unique_key, set_key, get_key, delete_key

CLIENTS = 100

def test_concurrent_sets_then_gets():
    keys = [unique_key("conc") for _ in range(CLIENTS)]
    values = [f"value-{i}" for i in range(CLIENTS)]

    with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
        set_results = list(executor.map(set_key, keys, values))
        get_results = list(executor.map(get_key, keys))

    assert all(r == (200, "ok") for r in set_results)
    assert get_results == [(200, v) for v in values]

def test_concurrent_writes_to_same_key():
    key = unique_key("contended")
    values = [f"writer-{i}" for i in range(CLIENTS)]

    with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
        results = list(executor.map(lambda v: set_key(key, v), values))

    assert all(r == (200, "ok") for r in results)

    status, final = get_key(key)
    assert status == 200
    assert final in values

def test_concurrent_mixed_commands():
    keys = [unique_key("mixed") for _ in range(CLIENTS)]

    def lifecycle(i):
        key = keys[i]
        value = f"v{i}"

        assert set_key(key, value) == (200, "ok")
        assert get_key(key) == (200, value)
        assert delete_key(key) == (200, "ok")
        assert get_key(key) == (200, "<none>")
        return True

    with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
        results = list(executor.map(lifecycle, range(CLIENTS)))

    assert all(results)


def test_concurrent_expiries():
    keys = [unique_key("exp") for _ in range(CLIENTS)]

    with ThreadPoolExecutor(max_workers=CLIENTS) as executor:
        results = list(executor.map(
            lambda k: set_key(k, "temp", expire_after_seconds=0.5), keys
        ))
        assert all(r == (200, "ok") for r in results)

        time.sleep(1)

        after = list(executor.map(get_key, keys))

    assert all(r == (200, "<none>") for r in after)
