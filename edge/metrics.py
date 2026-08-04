from edge.cache_logic import get_cache_size
from edge.config import CACHE_DIR

requests_total = 0
cache_hits = 0
cache_misses = 0
origin_fetches = 0
ratio = 0


def increment_requests():
    global requests_total
    requests_total += 1
    return {
            f"{requests_total}\n"
    }


def increment_cache_hit():
    global cache_hits
    cache_hits += 1
    return {
            f"{cache_hits}\n"
    }

def increment_cache_miss():
    global cache_misses 
    cache_misses += 1
    return {
            f"{cache_misses}\n"
    }

def increment_origin_fetch():
    global origin_fetches 
    origin_fetches += 1
    return {
            f"{origin_fetches}\n"
    }

def cache_size_mb(cache_dir):
    return round(get_cache_size(CACHE_DIR) / (1024 * 1024),2)

def cache_file_count(cache_dir):
    return sum(1 for file in cache_dir.iterdir() if file.is_file())


def get_metrics():
    if requests_total == 0:
        ratio = 0
    else:
        ratio = (cache_hits / requests_total) * 100
    return {
        "requests_total":requests_total, 
        "cache_hits":cache_hits ,
        "cache_misses":cache_misses, 
        "origin_fetches":origin_fetches, 
        "cache_hit_ratio_percent": round(ratio,2),
        "cache_size_mb": cache_size_mb(CACHE_DIR),
        "cache_file_count": cache_file_count(CACHE_DIR)
    }
