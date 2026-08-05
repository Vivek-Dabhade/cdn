import os
from dotenv import load_dotenv
from shared_utils.color_schema import log_info
from pathlib import Path

env_file = os.getenv("ENV_FILE", "configs/edge1.env")
load_dotenv(env_file)

CACHE_DIR = Path(os.getenv("CACHE_DIR")).resolve()
PORT = int(os.getenv("PORT", 3000))
CACHE_TTL = os.getenv("CACHE_TTL", 100) 
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", 1024))
ORIGIN_URL =os.getenv("ORIGIN_URL",'http://origin:3000')

# To create dirs autmatically.
CACHE_DIR.mkdir(parents=True, exist_ok=True)
