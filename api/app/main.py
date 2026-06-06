from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.middleware.gzip import GZipMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.routers import (
    arrests,
    context,
    crime_types,
    filters,
    geo,
    health,
    overview,
    pipeline,
    quality,
    timeseries,
)

app = FastAPI(
    title="Chicago Crime API",
    version="0.1.0",
    description="Public HTTP API exposing dbt marts for the Chicago Crime DBMS dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)

Instrumentator().instrument(app).expose(app)

app.include_router(overview.router, prefix="/api", tags=["overview"])
app.include_router(timeseries.router, prefix="/api", tags=["timeseries"])
app.include_router(geo.router, prefix="/api", tags=["geo"])
app.include_router(crime_types.router, prefix="/api", tags=["crime-types"])
app.include_router(arrests.router, prefix="/api", tags=["arrests"])
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(filters.router, prefix="/api", tags=["filters"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
app.include_router(quality.router, prefix="/api", tags=["quality"])
app.include_router(health.router, prefix="/api", tags=["system"])
