from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return {"message: Hello World!!"}

@app.get("/images/{filename}")
def show_image(filename : str):
    return FileResponse(f"origin/static/{filename}")
