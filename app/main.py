from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

from routers.api import router

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "DEBUG").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Resume Ranking API",
    description="API for extracting criteria from job descriptions and scoring resumes",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get(
    "/health",
    summary="Health Check",
    description="Returns the health status of the service.",
    response_description="A JSON object with the service status."
)
async def health_check():
    """
    Health check endpoint.

    This endpoint returns a JSON response indicating the current health status of the service.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8100)
