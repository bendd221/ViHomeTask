from fastapi import FastAPI
from routers import health, metrics

app = FastAPI(
    title="Vi Home Task Stocks Analytics",
)

app.include_router(health.router)
app.include_router(metrics.router)