import time
from pathlib import Path

CACHE_TTL = 10

def is_cache_valid(cached_file : Path):
    file_age = time.time() - cached_file.stat().st_mtime

    return file_age < CACHE_TTL
