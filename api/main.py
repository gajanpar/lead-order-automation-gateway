from datetime import datetime, timezone
import os
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="Order & Lead Automation Gateway",
    description="Validates incoming orders and dispatches events to n8n workflow engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/lead-ingest")


class LeadOrderIn(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100, example="Budi Pratama")
    customer_email: EmailStr = Field(..., example="budi@example.com")
    customer_whatsapp: str = Field(..., min_length=9, max_length=18, example="+6281234567890")
    service_type: Literal["custom_software", "workflow_automation", "consultation"] = Field(
        ..., example="workflow_automation"
    )
    budget_estimate_idr: float = Field(..., gt=0, example=3500000.0)
    notes: Optional[str] = Field(None, max_length=500, example="Integrasi Google Sheets dan WhatsApp")


class LeadOrderOut(BaseModel):
    status: str
    tracking_id: str
    received_at: str
    forwarded_to_n8n: bool


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "fastapi-gateway"}


@app.post("/api/v1/orders", response_model=LeadOrderOut, status_code=status.HTTP_201_CREATED)
async def create_lead_order(payload: LeadOrderIn):
    # Bersihkan nomor WhatsApp menjadi format standar internasional
    raw_wa = payload.customer_whatsapp.strip().replace(" ", "").replace("-", "")
    if raw_wa.startswith("0"):
        normalized_wa = "+62" + raw_wa[1:]
    elif raw_wa.startswith("62"):
        normalized_wa = "+" + raw_wa
    else:
        normalized_wa = raw_wa

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    tracking_id = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{abs(hash(payload.customer_email)) % 10000:04d}"

    event_payload = {
        "event": "lead_order_created",
        "tracking_id": tracking_id,
        "customer_name": payload.customer_name,
        "customer_email": payload.customer_email,
        "customer_whatsapp": normalized_wa,
        "service_type": payload.service_type,
        "budget_estimate_idr": payload.budget_estimate_idr,
        "notes": payload.notes or "-",
        "created_at": timestamp_iso,
    }

    forwarded = False
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(N8N_WEBHOOK_URL, json=event_payload)
            if resp.status_code in [200, 201]:
                forwarded = True
    except Exception:
        # Jika n8n belum aktif, request tetap diterima agar klien tidak error
        forwarded = False

    return LeadOrderOut(
        status="success",
        tracking_id=tracking_id,
        received_at=timestamp_iso,
        forwarded_to_n8n=forwarded,
    )
