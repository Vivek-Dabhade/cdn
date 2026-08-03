from fastapi import FastAPI, Response
import httpx
from load_balancer.config import EDGE_SERVERS
from pathlib import Path

current_edge = 0

app = FastAPI()

def select_edge():
    global current_edge
    edge = EDGE_SERVERS[current_edge]
    
    current_edge = (current_edge + 1) % len(EDGE_SERVERS)
    return edge


def forward_request(edge_url: str, filename: str):
    file_url = f"{edge_url}/files/{filename}"
    response = httpx.get(file_url)
    return response

@app.get("/files/{filename}")
def proxy_request(filename: str):
    edge = select_edge()
    response = forward_request(edge, filename)
    return Response(
        content = response.content,
        status_code = response.status_code,
        media_type = response.headers.get("content-type")
    )



