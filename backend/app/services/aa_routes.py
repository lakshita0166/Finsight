"""
aa_routes.py – FastAPI router for Account Aggregator endpoints.

Project layout:
    KAL/
    ├── setu_aa_client.py
    ├── fi_presets.py
    ├── fi_parser.py
    ├── main_data.py
    └── backend/
        └── app/
            └── services/
                └── aa_routes.py   ← this file

Endpoints consumed by Consent.jsx via aaAPI:
  POST   /api/aa/consent/create       ← ConsentModal "Create Consent & Link Accounts"
  GET    /api/aa/consent/me           ← aaAPI.getMyConsent()
  GET    /api/aa/consent/:id/status   ← aaAPI.getConsentStatus(consentId)
  POST   /api/aa/consent/:id/fetch    ← aaAPI.fetchData(consentId)
  DELETE /api/aa/consent/:id          ← aaAPI.revokeConsent(consentId)

Mount in your main FastAPI app:
    from app.services.aa_routes import router as aa_router
    app.include_router(aa_router)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

# ── Path fix: aa_routes.py is 3 levels deep inside KAL/  ─────────────────────
# __file__  = KAL/backend/app/services/aa_routes.py
# .parent   = KAL/backend/app/services/
# .parents[1] = KAL/backend/app/
# .parents[2] = KAL/backend/
# .parents[3] = KAL/                   ← project root with the AA files
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from setu_aa_client import SetuAAClient, SetuAAConfig
from fi_presets import PRESETS
from fi_parser import parse_session_response

logger = logging.getLogger("aa_routes")

router = APIRouter(prefix="/api/aa", tags=["account-aggregator"])

# ─────────────────────────────────────────────────────────────────────────────
# Config — identical credentials to main_data.py
# ─────────────────────────────────────────────────────────────────────────────
CONFIG = SetuAAConfig(
    client_id           = "ddd1cd58-afce-43b9-bcc9-ed10de775d3c",
    client_secret       = "JE6nZZH3wtfMX2BNPnxLOZ3bBWxAJfa0",
    product_instance_id = "cb266eb6-c770-4335-88f0-732fc391c58a",
    environment         = "sandbox",
    max_poll_attempts     = 20,
    poll_interval_seconds = 6,
)

# FI data JSON files are saved to KAL/ root — same location as main_data.py
DATA_DIR = _PROJECT_ROOT


def get_client() -> SetuAAClient:
    return SetuAAClient(CONFIG)


# ─────────────────────────────────────────────────────────────────────────────
# Request schemas
# ─────────────────────────────────────────────────────────────────────────────

class CreateConsentRequest(BaseModel):
    phone:  str   # e.g. "9876543210"
    aa:     str   # "onemoney" | "finvu" | "anumati"
    preset: str   # "banking" | "investments" | "credit" | "all" …


# ─────────────────────────────────────────────────────────────────────────────
# In-memory consent store (keyed by consent_id)
# Replace with your DB layer / user model as needed
# ─────────────────────────────────────────────────────────────────────────────
_consent_store: dict[str, dict] = {}

_AA_HANDLE = {
    "onemoney": "onemoney",
    "finvu":    "finvu",
    "anumati":  "anumati",
}


def _build_vua(phone: str, aa: str) -> str:
    """Build Virtual User Address:  <phone>@<aa_handle>"""
    handle = _AA_HANDLE.get(aa.lower(), aa.lower())
    return f"{phone}@{handle}"


# ─────────────────────────────────────────────────────────────────────────────
# Background task: mirrors Steps 3-5 from main_data.py demo_consent_and_data()
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_and_save(consent_id: str, client: SetuAAClient):
    """
    Runs in background once consent is ACTIVE.
    Output: KAL/fi_data_<consent_id[:8]>.json  (identical to main_data.py output)
    """
    try:
        logger.info("Background fetch started for consent=%s", consent_id)

        # Step 3 – resolve dataRange exactly as main_data.py does:
        # Use the stored original consent_resp first (has detail.dataRange guaranteed),
        # fall back to re-fetching from Setu if this session was created externally.
        stored       = _consent_store.get(consent_id, {})
        consent_resp = stored.get("consent_resp", {})

        consent_detail = consent_resp.get("detail", {})
        approved_range = consent_detail.get("dataRange", {})

        if approved_range.get("from") and approved_range.get("to"):
            data_from = datetime.fromisoformat(approved_range["from"].replace("Z", "+00:00"))
            data_to   = datetime.fromisoformat(approved_range["to"].replace("Z", "+00:00"))
            logger.info("Using consent_resp dataRange: %s -> %s", data_from.date(), data_to.date())
        else:
            # Fallback: re-fetch consent status (same as main_data.py's last-resort re-fetch)
            full_consent   = client.get_consent_status(consent_id)
            approved_range = full_consent.get("detail", {}).get("dataRange", {})
            if approved_range.get("from") and approved_range.get("to"):
                data_from = datetime.fromisoformat(approved_range["from"].replace("Z", "+00:00"))
                data_to   = datetime.fromisoformat(approved_range["to"].replace("Z", "+00:00"))
                logger.info("Using re-fetched dataRange: %s -> %s", data_from.date(), data_to.date())
            else:
                raise ValueError(
                    f"Could not read approved dataRange from consent {consent_id}. "
                    f"Response: {full_consent}"
                )

        session    = client.create_data_session(consent_id, data_from=data_from, data_to=data_to)
        session_id = session.get("id")
        logger.info("Data session created → %s", session_id)

        # Step 4 – poll until PARTIAL / COMPLETED
        fi_resp = client.wait_for_fi_data(session_id)
        logger.info("FI data received, status=%s", fi_resp.get("status"))

        # Step 5 – parse and save to KAL/fi_data_<id>.json
        parse_session_response(fi_resp)   # validates / logs structured output

        output_file = DATA_DIR / f"fi_data_{consent_id[:8]}.json"
        with open(output_file, "w") as fh:
            json.dump(fi_resp, fh, indent=2)
        logger.info("Raw FI data saved → %s", output_file)

        if consent_id in _consent_store:
            _consent_store[consent_id]["fetch_status"] = "done"
            _consent_store[consent_id]["data_file"]    = str(output_file)

    except Exception as exc:
        logger.exception("Background fetch failed for consent=%s: %s", consent_id, exc)
        if consent_id in _consent_store:
            _consent_store[consent_id]["fetch_status"] = "error"


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/consent/create")
async def create_consent(body: CreateConsentRequest):
    """
    ConsentModal → "Create Consent & Link Accounts".
    Returns webview_url — frontend must redirect the user there to approve.
    """
    preset_fn = PRESETS.get(body.preset)
    if not preset_fn:
        raise HTTPException(400, f"Unknown preset '{body.preset}'. Valid: {list(PRESETS)}")

    vua    = _build_vua(body.phone, body.aa)
    client = get_client()

    consent_req = preset_fn(vua)
    # After the user approves on the AA portal, Setu redirects them back here.
    # Must match your frontend /consent route exactly.
    consent_req.redirect_url = "http://localhost:5173/consent"   # ← update for production

    try:
        resp = client.create_consent(consent_req)
    except Exception as exc:
        logger.exception("create_consent failed")
        raise HTTPException(502, f"Setu API error: {exc}")

    consent_id  = resp["id"]
    webview_url = resp["url"]

    _consent_store[consent_id] = {
        "consent_id":     consent_id,
        "vua":            vua,
        "consent_status": "PENDING",
        "webview_url":    webview_url,
        "fetch_status":   None,
        "consent_resp":   resp,   # stored so _fetch_and_save can read detail.dataRange
    }

    return {
        "consent_id":  consent_id,
        "webview_url": webview_url,
        "status":      "PENDING",
        "vua":         vua,
    }


@router.get("/consent/me")
async def get_my_consent():
    """
    Consent.jsx calls this on mount (aaAPI.getMyConsent).
    Returns the most recent consent for the current user.
    Swap the stub below for a real DB lookup on your user record.
    """
    if not _consent_store:
        return {"consent_id": None}

    record = list(_consent_store.values())[-1]
    return {
        "consent_id":     record["consent_id"],
        "vua":            record.get("vua"),
        "consent_status": record["consent_status"],
        "status":         record["consent_status"],
    }


@router.get("/consent/{consent_id}/status")
async def get_consent_status(consent_id: str):
    """
    Consent.jsx polling loop (aaAPI.getConsentStatus).
    Proxies to Setu and updates local store.
    """
    client = get_client()
    try:
        resp   = client.get_consent_status(consent_id)
        status = resp.get("status", "PENDING")
    except Exception as exc:
        raise HTTPException(502, f"Setu API error: {exc}")

    if consent_id in _consent_store:
        _consent_store[consent_id]["consent_status"] = status

    return {"status": status, "consent_id": consent_id}


@router.post("/consent/{consent_id}/fetch")
async def fetch_data(consent_id: str, background_tasks: BackgroundTasks):
    """
    Consent.jsx calls this once consent turns ACTIVE (aaAPI.fetchData).
    Kicks off Steps 3-5 from main_data.py as a background task.
    Returns immediately so the frontend can show the loading state.
    """
    if consent_id not in _consent_store:
        _consent_store[consent_id] = {
            "consent_id":     consent_id,
            "consent_status": "ACTIVE",
            "fetch_status":   None,
        }

    _consent_store[consent_id]["fetch_status"] = "running"
    background_tasks.add_task(_fetch_and_save, consent_id, get_client())

    return {"status": "started", "consent_id": consent_id}


@router.delete("/consent/{consent_id}")
async def revoke_consent(consent_id: str):
    """
    Consent.jsx Revoke button (aaAPI.revokeConsent).
    """
    client = get_client()
    try:
        resp = client.revoke_consent(consent_id)
    except Exception as exc:
        raise HTTPException(502, f"Setu API error: {exc}")

    _consent_store.pop(consent_id, None)
    return resp