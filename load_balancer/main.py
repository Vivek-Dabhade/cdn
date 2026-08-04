from fastapi import FastAPI, Response, HTTPException
import httpx
from load_balancer.config import EDGE_SERVERS
from pathlib import Path

current_edge = 0

app = FastAPI()

def is_healthy(edge_url):
    global current_edge
    try:
        response = httpx.get(f"{edge_url}/health")
        return response.status_code == 200
    except httpx.RequestError:
        return False

def select_edge():
    global current_edge
    for _  in EDGE_SERVERS:
        each_edge = EDGE_SERVERS[current_edge]

        if is_healthy(each_edge):
            current_edge = (current_edge + 1) % len(EDGE_SERVERS)
            return each_edge
        else:
            current_edge = (current_edge + 1) % len(EDGE_SERVERS)
    raise HTTPException(
        status_code = 503,
        detail = "No healthy servers available.")


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


@app.get("/health")
def health():
    return {
        "service":"load-balancer",
        "status": "healthy"
    }


@app.get("/metrics")
def get_metrics():
    return aggregate_metrics()


def aggregate_metrics():
    totals = {
        "requests_total": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "origin_fetches": 0,
        "cache_size_mb": 0,
        "healthy_edges": 0,
        "total_edges": len(EDGE_SERVERS),
    }

    for edge in EDGE_SERVERS:

        try:
            response = httpx.get(f"{edge}/metrics")
            response.raise_for_status()

        except httpx.RequestError:
            continue

        totals["healthy_edges"] += 1

        response = httpx.get(f"{edge}/metrics")
        metrics = response.json()

        for key in (
            "requests_total",
            "cache_hits",
            "cache_misses",
            "origin_fetches",
            "cache_size_mb",
        ):
            totals[key] += metrics[key]

    if totals["requests_total"] == 0:
        totals["cache_hit_ratio_percent"] = 0
    else:
        totals["cache_hit_ratio_percent"] = round(
            (totals["cache_hits"] / totals["requests_total"]) * 100,
            2,
        )

    totals["cache_size_mb"] = round(totals["cache_size_mb"], 2)

    return totals
