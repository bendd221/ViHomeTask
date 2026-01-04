from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import health, metrics

app = FastAPI(
    title="Vi Home Task Stocks Analytics",
)

app.include_router(health.router)
app.include_router(metrics.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "path": request.url.path
        }
    )

logger.info("Server Started")