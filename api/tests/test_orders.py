import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

import main
from validators import normalize_whatsapp_number

client = TestClient(main.app)


def _valid_payload(**overrides):
    data = {
        "customer_name": "Rian Kusuma",
        "customer_email": "rian.kusuma@example.com",
        "customer_whatsapp": "081234567890",
        "service_type": "workflow_automation",
        "budget_estimate_idr": 4500000,
        "notes": "Connect incoming orders to internal workflow",
    }
    data.update(overrides)
    return data


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "fastapi-gateway"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("081234567890", "+6281234567890"),
        ("6281234567890", "+6281234567890"),
        ("+62 812-3456-7890", "+6281234567890"),
        ("+62 0812 3456 7890", "+6281234567890"),
        ("(0812) 345.6789", "+628123456789"),
        ("006281234567890", "+6281234567890"),
        ("+1 (415) 555-2671", "+14155552671"),
    ],
)
def test_normalize_whatsapp_number_valid(raw, expected):
    assert normalize_whatsapp_number(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "0812abc5678",
        "8123456789",
        "081234",
        "+62000123",
        "12345+67890",
    ],
)
def test_normalize_whatsapp_number_invalid(raw):
    with pytest.raises(ValueError):
        normalize_whatsapp_number(raw)


def test_create_order_forwarded_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_resp

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_ctx):
        resp = client.post("/api/v1/orders", json=_valid_payload(customer_whatsapp="(0812) 345-67890"))

    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "forwarded"
    assert body["forwarded_to_n8n"] is True
    assert body["tracking_id"].startswith("ORD-")
    uuid_part = body["tracking_id"].removeprefix("ORD-")
    assert uuid.UUID(uuid_part).version == 4

    sent_payload = mock_client_instance.post.call_args.kwargs["json"]
    assert sent_payload["customer_whatsapp"] == "+6281234567890"


def test_create_order_unforwarded_returns_202_and_honest_status(monkeypatch):
    monkeypatch.setattr(main, "STRICT_WEBHOOK_DELIVERY", False)

    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = httpx.ConnectError("n8n unreachable")

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_ctx):
        resp = client.post("/api/v1/orders", json=_valid_payload())

    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "accepted_unforwarded"
    assert body["forwarded_to_n8n"] is False
    assert "failed" in body["message"].lower()


def test_create_order_upstream_500_returns_202(monkeypatch):
    monkeypatch.setattr(main, "STRICT_WEBHOOK_DELIVERY", False)

    mock_resp = MagicMock()
    mock_resp.status_code = 500

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_resp

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_ctx):
        resp = client.post("/api/v1/orders", json=_valid_payload())

    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "accepted_unforwarded"
    assert body["forwarded_to_n8n"] is False


def test_create_order_strict_mode_returns_502_on_failure(monkeypatch):
    monkeypatch.setattr(main, "STRICT_WEBHOOK_DELIVERY", True)

    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = httpx.ReadTimeout("timeout")

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_ctx):
        resp = client.post("/api/v1/orders", json=_valid_payload())

    assert resp.status_code == 502
    assert "tracking_id" in resp.json()["detail"]


def test_tracking_ids_are_unique_for_identical_email():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_resp
    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_ctx):
        first = client.post("/api/v1/orders", json=_valid_payload()).json()["tracking_id"]
        second = client.post("/api/v1/orders", json=_valid_payload()).json()["tracking_id"]

    assert first != second


@pytest.mark.parametrize(
    "bad_override",
    [
        {"customer_email": "not-an-email"},
        {"service_type": "unknown_service"},
        {"budget_estimate_idr": 0},
        {"budget_estimate_idr": -500},
        {"customer_whatsapp": "invalid-phone"},
        {"notes": "x" * 501},
    ],
)
def test_validation_errors_return_422(bad_override):
    resp = client.post("/api/v1/orders", json=_valid_payload(**bad_override))
    assert resp.status_code == 422


def test_cors_blocks_unlisted_origin_and_disables_wildcard_credentials():
    assert "*" not in main.CORS_ORIGINS
    assert main.CORS_ALLOW_CREDENTIALS is False

    allowed = client.options(
        "/api/v1/orders",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    disallowed = client.options(
        "/api/v1/orders",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in disallowed.headers
