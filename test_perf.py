import time
import requests
import json

base_url = "http://localhost:8000"

def test_perf():
    start = time.time()
    for _ in range(10):
        resp = requests.get(f"{base_url}/regulations?page_size=100")
        resp.raise_for_status()
    print("Avg time:", (time.time() - start) / 10)

if __name__ == "__main__":
    test_perf()
