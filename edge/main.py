from fastapi import FastAPI, Response
import httpx
from pathlib import Path
from shared_utils.color_schema import log_error, log_info, log_warning
import mimetypes
from edge.cache_logic import is_cache_valid, update_last_access, file_eviction

app = FastAPI()

CACHE_DIR = Path("edge").resolve() / "cache"
ORIGIN = "http://localhost:8000"

# Downloading from origin
def fetch_from_origin(cached_file: Path, filename: str):
    response = httpx.get(f"{ORIGIN}/images/{filename}")

    # To avoid cache from saving corupted files
    if response.status_code == 200:
        cached_file.write_bytes(response.content)
    else:
        log_error(f"Origin returned: {response.status_code} {response.reason_phrase}")

    return response


@app.get("/files/{filename}")
def show_files(filename : str):
    
    cached_file = CACHE_DIR / filename

    file_eviction(CACHE_DIR, cached_file.stat().st_size)
    update_last_access(filename)
    
# Condition for cache hit
    if cached_file.exists():
        media_type, _ = mimetypes.guess_type(filename)

        # Checking if the cache is sitting for long than expected
        if is_cache_valid(cached_file) == True:
            log_info(f"CACHE HIT: {filename}")

        else:
            log_warning(f"The {filename} has expired. \nFetching from the origin")
            cached_file.unlink(missing_ok = True)
            fetch_from_origin(cached_file, filename)

        return Response(
            content = cached_file.read_bytes(),
            media_type = media_type
        )

# if cache missed
    else:
        log_warning(f"CACHE MISS: {filename}")
        response = fetch_from_origin(cached_file, filename)

        return Response(
            content = response.content,
            status_code = response.status_code,
            media_type = response.headers.get("content-type")
        )
