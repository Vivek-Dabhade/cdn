from edge.config import CACHE_DIR, PORT, EDGE_NAME

requests_total = 0
cache_hits = 0
cache_misses = 0
origin_fetches = 0

cache_hit_latency_total = 0.0
cache_hit_requests = 0

cache_miss_latency_total = 0.0
cache_miss_requests = 0

ttl_expirations = 0
evictions = 0


def increment_requests():
    global requests_total
    requests_total += 1


def increment_cache_hit():
    global cache_hits
    cache_hits += 1


def increment_cache_miss():
    global cache_misses
    cache_misses += 1


def increment_origin_fetch():
    global origin_fetches
    origin_fetches += 1


def increment_cache_hit_latency(elapsed_ms):
    global cache_hit_latency_total, cache_hit_requests

    cache_hit_latency_total += elapsed_ms
    cache_hit_requests += 1


def increment_cache_miss_latency(elapsed_ms):
    global cache_miss_latency_total, cache_miss_requests

    cache_miss_latency_total += elapsed_ms
    cache_miss_requests += 1


def increment_ttl_expiration():
    global ttl_expirations
    ttl_expirations += 1


def increment_eviction():
    global evictions
    evictions += 1


def cache_size_mb(cache_dir):
    from edge.cache_logic import get_cache_size

    return round(
        get_cache_size(cache_dir) / (1024 * 1024),
        2,
    )


def cache_file_count(cache_dir):
    return sum(
        1 for file in cache_dir.iterdir()
        if file.is_file()
    )


def average_cache_hit_latency_ms():
    if cache_hit_requests == 0:
        return 0

    return round(
        cache_hit_latency_total / cache_hit_requests,
        2,
    )


def average_cache_miss_latency_ms():
    if cache_miss_requests == 0:
        return 0

    return round(
        cache_miss_latency_total / cache_miss_requests,
        2,
    )


def get_metrics():

    if requests_total == 0:
        ratio = 0
    else:
        ratio = round(
            (cache_hits / requests_total) * 100,
            2,
        )

    return {
        "edge_name": f"{EDGE_NAME}-{PORT}",
        "requests_total": requests_total,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "origin_fetches": origin_fetches,
        "cache_hit_ratio_percent": ratio,
        "cache_size_mb": cache_size_mb(CACHE_DIR),
        "cache_file_count": cache_file_count(CACHE_DIR),
        "avg_cache_hit_latency_ms": average_cache_hit_latency_ms(),
        "avg_cache_miss_latency_ms": average_cache_miss_latency_ms(),
        "ttl_expirations": ttl_expirations,
        "evictions": evictions,
    }
