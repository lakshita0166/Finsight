"""
webhook_server.py – FastAPI webhook listener for Setu AA notifications.

Setu sends async notifications to your registered endpoint for:
  • CONSENT_STATUS_UPDATE  – when user approves / rejects consent
  • FI_DATA_READY          – when FI data is ready (with Auto-Fetch enabled)
  • SESSION_STATUS_UPDATE  – when a data session status changes

Run:
    pip install fastapi uvicorn
    uvicorn webhook_server:app --host 0.0.0.0 --port 8000 --reload

Configure https://<your-domain>/setu/notifications as your webhook on Bridge.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

logger = logging.getLogger("setu_aa.webhook")


try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse

    app = FastAPI(title="Setu AA Webhook Listener", version="1.0.0")

    # ── In-memory store (replace with DB in production) ───────────────────────
    _consent_events: list[Dict]  = []
    _fi_data_events: list[Dict]  = []
    _session_events: list[Dict]  = []

    @app.post("/setu/notifications")
    async def receive_notification(request: Request):
        """Main webhook endpoint registered on Setu Bridge."""
        try:
            payload: Dict[str, Any] = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON")

        notification_type = payload.get("type", "UNKNOWN")
        logger.info("Received notification type=%s  payload=%s", notification_type, json.dumps(payload, indent=2))

        if notification_type == "CONSENT_STATUS_UPDATE":
            _handle_consent_update(payload)
        elif notification_type == "FI_DATA_READY":
            _handle_fi_data_ready(payload)
        elif notification_type == "SESSION_STATUS_UPDATE":
            _handle_session_update(payload)
        else:
            logger.warning("Unknown notification type: %s", notification_type)

        # Setu expects a 200 OK acknowledgement
        return JSONResponse(status_code=200, content={"status": "received"})

    @app.get("/setu/consent-events")
    async def list_consent_events():
        return {"events": _consent_events}

    @app.get("/setu/fi-data-events")
    async def list_fi_data_events():
        return {"events": _fi_data_events}

    @app.get("/setu/session-events")
    async def list_session_events():
        return {"events": _session_events}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _handle_consent_update(payload: Dict):
        """
        Fired when user approves / rejects the consent.
        payload contains: consentId, status, timestamp
        """
        consent_id = payload.get("consentId")
        status     = payload.get("status")
        logger.info("Consent %s → %s", consent_id, status)
        _consent_events.append(payload)

        if status == "ACTIVE":
            logger.info("✅ Consent APPROVED – ready to create data session for %s", consent_id)
            # TODO: Trigger data session creation here
            # e.g. background_task.add_task(client.full_data_flow, consent_id)
        elif status in ("REJECTED", "REVOKED"):
            logger.warning("❌ Consent %s  status=%s", consent_id, status)

    def _handle_fi_data_ready(payload: Dict):
        """
        Fired by Setu Auto-Fetch when FI data is ready.
        payload contains: consentId, status, dataRange, fiData (decrypted)
        """
        consent_id = payload.get("consentId")
        status     = payload.get("status")
        fi_data    = payload.get("fiData", [])
        logger.info("FI_DATA_READY consent=%s  status=%s  fips=%d", consent_id, status, len(fi_data))
        _fi_data_events.append(payload)

        # TODO: Process fi_data and persist to your DB
        for fip_block in fi_data:
            fip_id   = fip_block.get("fipID")
            accounts = fip_block.get("data", [])
            for acc in accounts:
                masked = acc.get("maskedAccNumber")
                fi     = acc.get("decryptedFI", {})
                logger.info("  FIP=%s  acc=%s  txns=%d",
                            fip_id, masked,
                            len((fi.get("account", {}).get("transactions", {}).get("transaction") or [])))

    def _handle_session_update(payload: Dict):
        """Fired when a data session status changes."""
        session_id = payload.get("id") or payload.get("sessionId")
        status     = payload.get("status")
        logger.info("Session %s → %s", session_id, status)
        _session_events.append(payload)

except ImportError:
    # FastAPI not installed – provide a plain WSGI fallback for testing
    import http.server
    import socketserver

    class _SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                payload = json.loads(body)
                logger.info("Webhook received: %s", json.dumps(payload, indent=2))
            except Exception:
                logger.error("Failed to parse webhook body")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"received"}')

        def log_message(self, *_):
            pass

    def run_simple_server(port: int = 8000):
        with socketserver.TCPServer(("", port), _SimpleHandler) as httpd:
            logger.info("Simple webhook server on port %d (install fastapi for full support)", port)
            httpd.serve_forever()
