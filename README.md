# Mini-cdn-project

A lightweight Content Delivery Network (CDN) built from scratch using Python and FastAPI.

This project is being developed incrementally to understand the internal working of a CDN instead of relying on existing libraries or services.

Current Status: **Level 1 (In Progress)**

---

# Goals

- Learn HTTP request/response lifecycle
- Understand how CDNs serve content
- Implement caching from scratch
- Build a scalable architecture step by step
- Progress toward a distributed CDN

---

# Tech Stack

- Python
- FastAPI
- HTTPX
- pathlib
- mimetypes

---

# Project Structure

```
mini-cdn/
│
├── origin/
│   ├── main.py
│   └── static/
│       └── quote.jpeg
│
├── edge/
│   ├── main.py
│   ├── cache/
│   └── cache_logic.py
│
└── shared_utils/
```

---

# Current Architecture

```
                Browser
                    │
            GET /images/file
                    │
                    ▼
          Edge Server (8001)
                    │
        ┌───────────┴────────────┐
        │                        │
   Cache HIT                Cache MISS
        │                        │
        ▼                        ▼
 Serve Cached File      Fetch From Origin
        │                        │
        │                  Origin Server
        │                  (localhost:8000)
        │                        │
        └──────────────┬─────────┘
                       │
                Store in Cache
                       │
                       ▼
                   Browser
```

---

# Request Flow

## Cache Miss

```
Browser
    │
    ▼
Edge
    │
    ▼
Cache Exists?
    │
    ├── No
    │
    ▼
Origin
    │
    ▼
Download File
    │
    ▼
Save to Cache
    │
    ▼
Return Response
```

---

## Cache Hit

```
Browser
    │
    ▼
Edge
    │
    ▼
Cache Exists?
    │
    ├── Yes
    │
    ▼
Serve Cached File
    │
    ▼
Browser
```

---

# Features Implemented

## Origin Server

- FastAPI server
- Dynamic image route
- Static file serving
- HTTP error handling

Example endpoint

```
GET /images/{filename}
```

---

## Edge Server

Acts as a reverse proxy.

Responsibilities

- Receives browser requests
- Checks local cache
- Downloads missing files
- Returns HTTP response
- Preserves content type

---

# Cache

Implemented

- Cache HIT detection
- Cache MISS detection
- Local file storage
- Local file retrieval
- MIME type detection

Cache directory

```
edge/
└── cache/
```

---

# TTL (Time To Live)

Implemented

- Cache expiration
- Automatic refresh from origin
- Expired cache removal

Flow

```
Cache Exists?
      │
      ▼
Check TTL
      │
 ┌────┴────┐
 │         │
Valid   Expired
 │         │
 │         ▼
 │    Delete File
 │         │
 │         ▼
 └──► Fetch Origin
           │
           ▼
      Save Cache
```

---

# Error Handling

Implemented

- Do not cache failed origin responses
- Preserve HTTP status codes
- Preserve response headers

Example

```
Origin -> 404

↓

Edge returns 404

↓

Nothing is cached
```

---

# Cache Metadata (In Progress)

Started implementing cache metadata for future LRU support.

Current idea

```
last_accessed = {
    "quote.jpeg": timestamp,
    "image.png": timestamp
}
```

This metadata will be used for cache eviction.

---

# Concepts Learned

- HTTP Request/Response
- Origin Server
- Edge Server
- Reverse Proxy
- MIME Types
- Cache HIT
- Cache MISS
- TTL
- File Storage
- Response Forwarding
- Refactoring Cache Logic

---

# Future Roadmap

## Cache

- [ ] LRU Eviction
- [ ] Maximum Cache Size

## Networking

- [ ] Multiple Edge Servers
- [ ] Geo Routing
- [ ] Router Service

## Monitoring

- [ ] Cache Metrics
- [ ] Hit Ratio
- [ ] Dashboard

## Deployment

- [ ] Docker
- [ ] Nginx
- [ ] Prometheus
- [ ] Grafana

---

# Progress

| Module | Status |
|---------|--------|
| HTTP Basics | ✅ |
| Origin Server | ✅ |
| Edge Server | ✅ |
| Cache HIT/MISS | ✅ |
| MIME Detection | ✅ |
| TTL | ✅ |
| Error Handling | ✅ |
| Cache Metadata | 🚧 |
| LRU | ⏳ |
| Multiple Edges | ⏳ |
| Geo Routing | ⏳ |

---

# Learning Objective

This project is intentionally built incrementally to understand the internal architecture of modern CDNs rather than simply using existing frameworks or cloud services.
