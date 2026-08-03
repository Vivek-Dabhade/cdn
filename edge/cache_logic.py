import time
from pathlib import Path
from shared_utils.color_schema import log_info
from edge.config import CACHE_TTL, MAX_CACHE_SIZE

last_accessed = {}

# Checking if the file is loger than expected
def is_cache_valid(cached_file : Path):
    file_age = time.time() - cached_file.stat().st_mtime

    return file_age < float(CACHE_TTL)

# filling up the last_accessed
def update_last_access(filename: str):
    last_accessed[filename] = time.time()

def get_cache_size(cache_dir: Path):
    total_cache_size = 0
    for files in cache_dir.rglob('*'):
        total_cache_size += files.stat().st_size
    return total_cache_size

# LRU - least recently used
# When size limit is exceeded which file needs to be deleted
def file_eviction(cache_dir: Path, incoming_file_size: float):
        free_mem = MAX_CACHE_SIZE - get_cache_size(cache_dir)

        while float(free_mem) < incoming_file_size :
            if not last_accessed:
                return False

            oldest_file = min(last_accessed, key = last_accessed.get)
            delete_file = cache_dir / str(oldest_file)

            if delete_file.is_file(): 
                free_mem += delete_file.stat().st_size
                delete_file.unlink(missing_ok = True)
                log_info(f"Cache-maintainance pruning {delete_file}")

            last_accessed.pop(oldest_file)

        return True
