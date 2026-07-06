import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.api.routes import auth, health, market, order_alias, orders, portfolio, positions, ws
from src.config.settings import get_settings
from src.core.logging import configure_logging
from src.core.metrics import API_CALLS, LATENCY
from src.core.rate_limiter import rate_limiter
from src.workers.alert_subscriber import run_alert_subscriber
from src.websocket.market_stream import stream_market_data

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    tasks = []
    if get_settings().enable_background_workers:
        tasks = [
            asyncio.create_task(stream_market_data(stop_event)),
            asyncio.create_task(run_alert_subscriber(stop_event)),
        ]
    logger.info("service_started")
    try:
        yield
    finally:
        stop_event.set()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("service_stopped")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Unified crypto exchange backend with paper order execution.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_and_rate_limit(request: Request, call_next):
    await rate_limiter(request)
    with LATENCY.labels(operation="api.request").time():
        response = await call_next(request)
    API_CALLS.labels(route=request.url.path, method=request.method, status=response.status_code).inc()
    return response


app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(orders.router)
app.include_router(order_alias.router)
app.include_router(positions.router)
app.include_router(market.router)
app.include_router(ws.router)
app.include_router(health.router)
