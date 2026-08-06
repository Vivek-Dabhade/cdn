from fastapi import FastAPI, Response
import httpx
from pathlib import Path
from shared_utils.color_schema import log_error, log_info, log_warning
import mimetypes
from edge.cache_logic import is_cache_valid, update_last_access, file_eviction
from edge.config import ORIGIN_URL, CACHE_DIR
from edge.metrics import increment_origin_fetch, increment_cache_hit, increment_cache_miss, get_metrics, increment_requests, increment_cache_hit_latency, increment_cache_miss_latency, increment_ttl_expiration
import time
import threading

_write_lock = threading.Lock()

app = FastAPI()

@app.get("/files/{filename}")
def show_files(filename : str):
    increment_requests()
    cached_file = CACHE_DIR / filename
    start = time.perf_counter()
    
# Condition for cache hit
    if cached_file.exists():
        media_type, _ = mimetypes.guess_type(filename)

        # Checking if the cache is sitting for long than expected
        if is_cache_valid(cached_file) == True:
            update_last_access(filename)
            log_info(f"CACHE HIT: {filename}")
            increment_cache_hit()

            # Checking time performance.
            elapsed = (time.perf_counter() - start) * 1000
            increment_cache_hit_latency(elapsed)

        else:
            update_last_access(filename)
            log_warning(f"The {filename} has expired. \nFetching from the origin")
            increment_ttl_expiration()
            # cached_file.unlink(missing_ok = True)       will not be needed because the write_bytes will overwrite the same file if present.
            response = fetch_from_origin(cached_file, filename)
            if response is None or response.status_code != 200:
                log_warning(f"Serving stale {filename} — origin unreachable")
            increment_cache_miss()

            elapsed = (time.perf_counter() - start) * 1000
            increment_cache_miss_latency(elapsed)

        return Response(
            content = cached_file.read_bytes(),
            media_type = media_type
        )

# if cache missed
    else:
        log_warning(f"CACHE MISS: {filename}")
        response = fetch_from_origin(cached_file, filename)
        update_last_access(filename)
        increment_cache_miss()
        elapsed = (time.perf_counter() - start) * 1000
        increment_cache_miss_latency(elapsed)
    
        if response is None:
            return Response(
                content=b"Origin server unavailable.",
                status_code=502,
                media_type="text/plain",
            )
    
        return Response(
            content = response.content,
            status_code = response.status_code,
            media_type = response.headers.get("content-type")
        )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/metrics")
def metrics():
    return get_metrics()


# Downloading from origin
def fetch_from_origin(cached_file: Path, filename: str):
    # To avoid cache from saving corrupted files
    try:
        response = httpx.get(f"{ORIGIN_URL}/images/{filename}", timeout=5.0)
    except httpx.RequestError as exc:
        log_error(f"Origin unreachable for {filename}: {exc}")
        return None

    increment_origin_fetch()

    if response.status_code == 200:
        with _write_lock:
            file_eviction(CACHE_DIR, len(response.content))
            cached_file.write_bytes(response.content)
        return response

