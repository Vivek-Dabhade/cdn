from fastapi import FastAPI, Response
import httpx
from pathlib import Path
from shared_utils.color_schema import log_error, log_info, log_warning
import mimetypes
from edge.cache_logic import is_cache_valid

app = FastAPI()

CACHE_DIR = Path("edge").resolve() / "cache"
ORIGIN = "http://localhost:8000"

@app.get("/files/{filename}")
def show_files(filename : str):
    
    cached_file = CACHE_DIR / filename
    if cached_file.exists():
        media_type, _ = mimetypes.guess_type(filename)
        if is_cache_valid(cached_file) == True:
            log_info(f"CACHE HIT: {filename}")

        else:
            log_warning(f"The {filename} has expired \nFetching from the origin")
            cached_file.unlink(missing_ok = True)
            response = httpx.get(f"{ORIGIN}/images/{filename}")

            if response.status_code == 200:
                cached_file.write_bytes(response.content)

        return Response(
            content = cached_file.read_bytes(),
            media_type = media_type
        )

    else:
        log_warning(f"CACHE MISS: {filename}")

        response = httpx.get(f"{ORIGIN}/images/{filename}")

        # Need to protect the cache from storing corrupt files
        if response.status_code == 200:
            cached_file.write_bytes(response.content)
        else:
            log_error(f"Origin returned {response.status_code}")

        return Response(
            content = response.content,
            status_code = response.status_code,
            media_type = response.headers.get("content-type")
        )
