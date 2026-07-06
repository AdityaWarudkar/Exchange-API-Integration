from fastapi import APIRouter
from fastapi.responses import Response

from src.core.metrics import metrics_response

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "exchange-api-order-execution-sandbox"}


@router.get("/metrics")
async def metrics():
    return Response(metrics_response(), media_type="text/plain; version=0.0.4")

