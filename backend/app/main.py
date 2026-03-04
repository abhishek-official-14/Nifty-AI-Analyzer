"""FastAPI entrypoint for Nifty AI Analyzer Pro backend."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Nifty AI Analyzer Pro API",
    version="1.0.0",
    description="Backend core for AI-powered trading analytics across technical, fundamental, and market breadth signals.",
)

app.include_router(router)


@app.get("/")
def health() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok", "service": "Nifty AI Analyzer Pro"}
