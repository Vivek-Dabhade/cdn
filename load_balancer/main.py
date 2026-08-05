from fastapi import FastAPI, Response, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
from load_balancer.config import EDGE_POOLS, ROUND_ROBIN_INDEX
from pathlib import Path


app = FastAPI()

region_requests = {
    "india": 0,
    "europe": 0,
    "default": 0,
}

failovers = 0


@app.get("/files/{filename}")
def proxy_request(
    filename: str,
    x_region: str | None = Header(default=None),
):

    region = (x_region or "default").lower()
    if region not in region_requests:
        region = "default"
    region_requests[region] += 1
    
    region, pool = get_edge_pool(region)
    edge = select_edge(region, pool)
    response = forward_request(edge, filename)
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type"),
        headers={
            "X-Served-By": edge,
            "X-Selected-Region": region,
        },
    )


@app.get("/health")
def health():
    return {
        "service":"load-balancer",
        "status": "healthy"
    }

@app.get("/metrics")
def get_metrics():
    return JSONResponse(
        content=aggregate_metrics(),
        media_type="application/json"
    )

def get_edge_pool(region):
    region = region.lower()

    if region not in EDGE_POOLS:
        region = "default"

    return region, EDGE_POOLS[region]

def is_healthy(edge_url):
    try:
        response = httpx.get(f"{edge_url}/health")
        return response.status_code == 200
    except httpx.RequestError:
        return False

def select_edge(region, pool):
    global failovers

    curr_index = ROUND_ROBIN_INDEX[region]
    starting_index = curr_index

    for _ in pool:
        each_edge = pool[curr_index]

        if is_healthy(each_edge):

            if curr_index != starting_index:
                failovers += 1

            ROUND_ROBIN_INDEX[region] = (curr_index + 1) % len(pool)
            return each_edge

        curr_index = (curr_index + 1) % len(pool)

    raise HTTPException(
        status_code=503,
        detail="No healthy servers available."
    )


def forward_request(edge_url: str, filename: str):
    file_url = f"{edge_url}/files/{filename}"
    response = httpx.get(file_url)
    return response


def aggregate_metrics():
    totals = {
        "requests_total": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "origin_fetches": 0,
        "cache_size_mb": 0,
        "healthy_edges": 0,
        "total_edges": 0,
    }
    totals["region_requests"] = region_requests.copy()
    totals["failovers"] = failovers
    
    for pools in EDGE_POOLS.values():
        for edge in pools:

            totals["total_edges"] += 1
            try:
                response = httpx.get(f"{edge}/metrics")
                response.raise_for_status()
    
            except httpx.RequestError:
                continue
    
            totals["healthy_edges"] += 1
    
            # response = httpx.get(f"{edge}/metrics")
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
