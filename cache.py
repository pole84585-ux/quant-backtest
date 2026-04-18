import json
import os

CACHE_FILE = "tg_cache.json"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return set()

    try:
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)
