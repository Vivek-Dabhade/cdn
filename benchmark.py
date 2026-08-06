"""
Realistic CDN benchmark: Zipfian request distribution + real concurrency.

Usage:
    python3 benchmark.py --url http://localhost:9000 --files origin/static \
        --requests 5000 --concurrency 50

This is NOT the same as hitting one file in a loop. ~20% of files get ~80%
of traffic (hot set), the rest get requested rarely (cold/long tail) -- this
is what actually exercises LRU eviction the way production traffic would.
"""
import argparse
import concurrent.futures
import random
import time
import os
import httpx

def zipf_weights(n, s=1.2):
    weights = [1 / (i ** s) for i in range(1, n + 1)]
    total = sum(weights)
    return [w / total for w in weights]

def run(url, files_dir, total_requests, concurrency, region):
    filenames = [f for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))]
    if not filenames:
        raise SystemExit(f"No files found in {files_dir}")

    random.shuffle(filenames)
    weights = zipf_weights(len(filenames))
    request_plan = random.choices(filenames, weights=weights, k=total_requests)

    latencies = []
    errors = 0

    def do_request(fname):
        nonlocal errors
        client = httpx.Client(timeout=10.0)
        try:
            t0 = time.perf_counter()
            resp = client.get(f"{url}/files/{fname}", headers={"X-Region": region})
            elapsed = (time.perf_counter() - t0) * 1000
            if resp.status_code != 200:
                errors += 1
            return elapsed
        except httpx.RequestError:
            errors += 1
            return None
        finally:
            client.close()

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        for result in pool.map(do_request, request_plan):
            if result is not None:
                latencies.append(result)
    duration = time.time() - start

    latencies.sort()
    def pct(p):
        if not latencies:
            return 0
        idx = min(int(len(latencies) * p / 100), len(latencies) - 1)
        return round(latencies[idx], 2)

    print(f"Total requests:     {total_requests}")
    print(f"Unique files used:  {len(filenames)} (Zipfian weighted)")
    print(f"Concurrency:        {concurrency}")
    print(f"Duration:           {round(duration, 2)}s")
    print(f"Requests/sec:       {round(total_requests / duration, 2)}")
    print(f"Errors:             {errors}")
    print(f"Latency avg:        {round(sum(latencies)/len(latencies), 2) if latencies else 0} ms")
    print(f"Latency p50/p90/p99: {pct(50)} / {pct(90)} / {pct(99)} ms")
    print()
    print("Now fetch http://<load_balancer>:9000/metrics for hit ratio, failovers, healthy_edges")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:9000")
    ap.add_argument("--files", default="origin/static")
    ap.add_argument("--requests", type=int, default=5000)
    ap.add_argument("--concurrency", type=int, default=50)
    ap.add_argument("--region", default="india")
    args = ap.parse_args()
    run(args.url, args.files, args.requests, args.concurrency, args.region)
