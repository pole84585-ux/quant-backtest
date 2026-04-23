import requests
import time

def safe_get(url, params=None, retries=3, timeout=8):

    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            return r.json() if "json" in r.headers.get("Content-Type","") else r.text

        except Exception as e:
            print(f"[NET retry {i}] {e}")
            time.sleep(2)

    return None
