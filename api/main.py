from datetime import datetime, timezone
import logging
import os
from typing import Literal, Optional
import uuid

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel, EmailStr, Field, field_validator

from validators import normalize_whatsapp_number

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("lead_gateway")


def _parse_cors_origins(raw_origins: str) -> list[str]:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]


CORS_ORIGINS = _parse_cors_origins(
    os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000",
    )
)
CORS_ALLOW_CREDENTIALS = (
    os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true" and "*" not in CORS_ORIGINS
)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/lead-ingest")
N8N_TIMEOUT_SECONDS = float(os.getenv("N8N_TIMEOUT_SECONDS", "4.0"))
STRICT_WEBHOOK_DELIVERY = os.getenv("STRICT_WEBHOOK_DELIVERY", "false").lower() == "true"

app = FastAPI(
    title="Order & Lead Automation Gateway",
    description="Validates incoming orders and dispatches events to n8n workflow engine.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)


class LeadOrderIn(BaseModel):
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        json_schema_extra={"example": "Budi Pratama"},
    )
    customer_email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "budi@example.com"},
    )
    customer_whatsapp: str = Field(
        ...,
        min_length=9,
        max_length=22,
        json_schema_extra={"example": "+6281234567890"},
    )
    service_type: Literal["custom_software", "workflow_automation", "consultation"] = Field(
        ...,
        json_schema_extra={"example": "workflow_automation"},
    )
    budget_estimate_idr: float = Field(
        ...,
        gt=0,
        json_schema_extra={"example": 3500000.0},
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        json_schema_extra={"example": "Integrasi order ke workflow internal"},
    )

    @field_validator("customer_whatsapp")
    @classmethod
    def validate_and_normalize_whatsapp(cls, value: str) -> str:
        return normalize_whatsapp_number(value)


class LeadOrderOut(BaseModel):
    status: Literal["forwarded", "accepted_unforwarded"]
    message: str
    tracking_id: str
    received_at: str
    forwarded_to_n8n: bool


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "fastapi-gateway"}


@app.post(
    "/api/v1/orders",
    response_model=LeadOrderOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": LeadOrderOut,
            "description": "Order accepted by API, but downstream forwarding to n8n failed.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "description": "Downstream n8n webhook delivery failed when STRICT_WEBHOOK_DELIVERY=true.",
        },
    },
)
async def create_lead_order(payload: LeadOrderIn, response: Response):
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    tracking_id = f"ORD-{uuid.uuid4()}"

    event_payload = {
        "event": "lead_order_created",
        "tracking_id": tracking_id,
        "customer_name": payload.customer_name,
        "customer_email": payload.customer_email,
        "customer_whatsapp": payload.customer_whatsapp,
        "service_type": payload.service_type,
        "budget_estimate_idr": payload.budget_estimate_idr,
        "notes": payload.notes or "-",
        "created_at": timestamp_iso,
    }

    forwarded = False
    failure_reason = ""
    try:
        async with httpx.AsyncClient(timeout=N8N_TIMEOUT_SECONDS) as client:
            resp = await client.post(N8N_WEBHOOK_URL, json=event_payload)
            if 200 <= resp.status_code < 300:
                forwarded = True
            else:
                failure_reason = f"upstream returned HTTP {resp.status_code}"
    except httpx.HTTPError as exc:
        failure_reason = exc.__class__.__name__

    if forwarded:
        logger.info("order_forwarded tracking_id=%s", tracking_id)
        response.status_code = status.HTTP_201_CREATED
        return LeadOrderOut(
            status="forwarded",
            message="Order received and forwarded to the n8n workflow.",
            tracking_id=tracking_id,
            received_at=timestamp_iso,
            forwarded_to_n8n=True,
        )

    logger.warning(
        "order_forward_failed tracking_id=%s reason=%s",
        tracking_id,
        failure_reason or "unknown",
    )
    if STRICT_WEBHOOK_DELIVERY:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Downstream n8n webhook delivery failed.",
                "tracking_id": tracking_id,
                "reason": failure_reason,
            },
        )

    response.status_code = status.HTTP_202_ACCEPTED
    return LeadOrderOut(
        status="accepted_unforwarded",
        message="Order accepted by API, but forwarding to n8n failed. Downstream processing is not guaranteed.",
        tracking_id=tracking_id,
        received_at=timestamp_iso,
        forwarded_to_n8n=False,
    )
