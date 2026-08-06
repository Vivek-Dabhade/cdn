from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import HTTPException

app = FastAPI()

@app.get("/")
def home():
    return {message: "Hello World!!"}

@app.get("/images/{filename}")
def show_image(filename: str):
    file_path = Path(f"origin/static/{filename}")

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="The requested configuration file is missing."
        )

    return FileResponse(file_path)
