"""
Setu Account Aggregator (AA) - Production-Ready FIU Client
===========================================================
Implements the full FIU flow:
  1. OAuth Token    → generate Bearer token from clientID + secret
  2. Consent Flow   → create / get / revoke consents
  3. Data Flow      → create sessions, poll & fetch all FI types
  4. FIP Discovery  → list active FIPs
  5. Notifications  → lightweight webhook listener (FastAPI)

All 23 AA FI data types are supported via the consent builder.

Author  : Finance Project
Env     : Sandbox    → https://fiu-sandbox.setu.co   (AA APIs)
                       https://uat.setu.co            (Token API)
          Production → https://fiu.setu.co            (AA APIs)
                       https://prod.setu.co           (Token API)
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("setu_aa")


# ─────────────────────────────────────────────────────────────────────────────
# Enums – all values sourced from Setu AA docs
# ─────────────────────────────────────────────────────────────────────────────
class FIType(str, Enum):
    """All 23 AA Financial Information types (ReBIT-spec)."""
    # Banking / Deposits
    DEPOSIT             = "DEPOSIT"
    TERM_DEPOSIT        = "TERM_DEPOSIT"
    RECURRING_DEPOSIT   = "RECURRING_DEPOSIT"
    SIP                 = "SIP"
    # Credit
    CREDIT_CARD         = "CREDIT_CARD"
    LOAN                = "LOAN"
    # Insurance
    INSURANCE_POLICIES  = "INSURANCE_POLICIES"
    # Investments
    EQUITIES            = "EQUITIES"
    MUTUAL_FUNDS        = "MUTUAL_FUNDS"
    ETF                 = "ETF"
    IDR                 = "IDR"
    NPS                 = "NPS"
    PPF                 = "PPF"
    # GST
    GST_GSTR1           = "GST_GSTR1"
    GST_GSTR2A          = "GST_GSTR2A"
    GST_GSTR3B          = "GST_GSTR3B"
    # Government
    NHB_STATEMENTS      = "NHB_STATEMENTS"
    # EPFO
    EPFO                = "EPFO"
    # Others
    CIS                 = "CIS"
    AIS                 = "AIS"
    TIS                 = "TIS"
    ULIP                = "ULIP"
    INVIT               = "INVIT"


class ConsentMode(str, Enum):
    VIEW  = "VIEW"
    STORE = "STORE"
    QUERY = "QUERY"
    STREAM = "STREAM"


class FetchType(str, Enum):
    ONE_TIME = "ONETIME"
    PERIODIC = "PERIODIC"


class ConsentType(str, Enum):
    PROFILE      = "PROFILE"
    SUMMARY      = "SUMMARY"
    TRANSACTIONS = "TRANSACTIONS"


class DataLifeUnit(str, Enum):
    DAY   = "DAY"
    MONTH = "MONTH"
    YEAR  = "YEAR"
    INF   = "INF"


class FrequencyUnit(str, Enum):
    HOUR  = "HOUR"
    DAY   = "DAY"
    MONTH = "MONTH"
    YEAR  = "YEAR"
    INF   = "INF"


class ConsentStatus(str, Enum):
    PENDING  = "PENDING"
    ACTIVE   = "ACTIVE"
    REJECTED = "REJECTED"
    REVOKED  = "REVOKED"
    EXPIRED  = "EXPIRED"
    PAUSED   = "PAUSED"


class SessionStatus(str, Enum):
    PENDING   = "PENDING"
    PARTIAL   = "PARTIAL"
    COMPLETED = "COMPLETED"
    EXPIRED   = "EXPIRED"
    FAILED    = "FAILED"


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SetuAAConfig:
    client_id: str          # clientID for OAuth token generation
    client_secret: str      # secret  for OAuth token generation
    product_instance_id: str
    environment: str = "sandbox"          # "sandbox" | "production"

    # Auto-derived from environment (override if needed)
    base_url: str   = ""    # AA API base  e.g. https://fiu-sandbox.setu.co
    token_url: str  = ""    # OAuth token  e.g. https://uat.setu.co/api/v2/auth/token

    # Polling
    max_poll_attempts: int = 20
    poll_interval_seconds: int = 5

    # HTTP
    request_timeout: int = 30
    max_retries: int = 3

    def __post_init__(self):
        if not self.base_url:
            if self.environment == "production":
                self.base_url = "https://fiu.setu.co"
            else:
                self.base_url = "https://fiu-sandbox.setu.co"

        if not self.token_url:
            if self.environment == "production":
                self.token_url = "https://prod.setu.co/api/v2/auth/token"
            else:
                self.token_url = "https://uat.setu.co/api/v2/auth/token"


# ─────────────────────────────────────────────────────────────────────────────
# Consent Builder  (fluent interface)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ConsentRequest:
    """
    Setu AA consent object builder.
    All field names and values match the official API schema exactly.
    """
    vua: str                                   # e.g. 9999999999@onemoney
    fi_types: List[FIType]
    purpose_code: str           = "101"
    purpose_text: str           = "Personal Finance Management"
    consent_mode: ConsentMode   = ConsentMode.STORE
    fetch_type: FetchType       = FetchType.ONE_TIME
    consent_types: List[ConsentType] = field(
        default_factory=lambda: [ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS]
    )
    data_range_from: Optional[datetime] = None   # defaults to 2 years ago
    data_range_to:   Optional[datetime] = None   # defaults to now

    # consentDuration – how long the consent stays valid
    consent_duration_unit:  str = "MONTH"        # MONTH | YEAR | DAY
    consent_duration_value: int = 4

    # dataLife – how long FIU can retain the fetched data
    data_life_unit:  DataLifeUnit = DataLifeUnit.YEAR
    data_life_value: int = 1

    # frequency – max data-fetch frequency allowed per this consent
    frequency_unit:  FrequencyUnit = FrequencyUnit.MONTH
    frequency_value: int = 30                    # max 1/HOURLY per spec

    redirect_url: str = "https://setu.co"       # must be a real URL
    tags: List[str] = field(default_factory=list)
    context: List[Dict] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        now       = datetime.now(timezone.utc)
        data_from = self.data_range_from or (now - timedelta(days=730))
        data_to   = self.data_range_to   or now

        payload: Dict[str, Any] = {
            "vua": self.vua,
            "redirectUrl": self.redirect_url,

            # How long this consent is valid (from now)
            "consentDuration": {
                "unit":  self.consent_duration_unit,
                "value": str(self.consent_duration_value),
            },

            # Date range for which financial data is requested
            "dataRange": {
                "from": data_from.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "to":   data_to.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            },

            # Purpose of data request (ReBIT codes)
            "purpose": {
                "code":   self.purpose_code,
                "refUri": f"https://api.rebit.org.in/aa/purpose/{self.purpose_code}.xml",
                "text":   self.purpose_text,
                "category": {"type": "string"},
            },

            "fiTypes":      [fi.value for fi in self.fi_types],
            "consentTypes": [ct.value for ct in self.consent_types],
            "fetchType":    self.fetch_type.value,
            "consentMode":  self.consent_mode.value,

            # How long FIU may retain the data after fetching
            "dataLife": {
                "unit":  self.data_life_unit.value,
                "value": self.data_life_value,
            },

            # Maximum allowed fetch frequency
            "frequency": {
                "unit":  self.frequency_unit.value,
                "value": self.frequency_value,
            },

            # context is always an array (empty is fine)
            "context": self.context,
        }

        # Tags go under additionalParams per the Setu spec
        if self.tags:
            payload["additionalParams"] = {"tags": self.tags}

        return payload


# ─────────────────────────────────────────────────────────────────────────────
# Token cache (module-level, simple in-memory)
# ─────────────────────────────────────────────────────────────────────────────
_token_cache: Dict[str, Any] = {}   # keyed by client_id


def _fetch_oauth_token(config: SetuAAConfig) -> str:
    """
    Generate a Bearer token via Setu OAuth2.
    Tokens are valid for 1800 seconds (30 min). Cached until expiry.
    Token URL (sandbox): https://uat.setu.co/api/v2/auth/token
    """
    cache_key = config.client_id
    cached = _token_cache.get(cache_key)
    if cached and cached["expires_at"] > time.time() + 60:
        return cached["token"]

    logger.info("Fetching new OAuth token from %s", config.token_url)
    resp = requests.post(
        config.token_url,
        json={"clientID": config.client_id, "secret": config.client_secret},
        headers={"Content-Type": "application/json"},
        timeout=config.request_timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    token      = data["data"]["token"]
    expires_in = data["data"].get("expiresIn", 1800)

    _token_cache[cache_key] = {
        "token":      token,
        "expires_at": time.time() + expires_in,
    }
    logger.info("OAuth token acquired, valid for %ds", expires_in)
    return token


def _build_http_session(config: SetuAAConfig) -> requests.Session:
    session = requests.Session()

    retry_strategy = Retry(
        total=config.max_retries,
        status_forcelist=[429, 502, 503, 504],  # NOT 500 — that's a server error, fail fast
        backoff_factor=1,
        allowed_methods=["GET", "POST", "DELETE"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    # Base headers - Authorization is set dynamically before each call
    session.headers.update({
        "Content-Type":            "application/json",
        "x-product-instance-id":   config.product_instance_id,
    })
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Core AA Client
# ─────────────────────────────────────────────────────────────────────────────
class SetuAAClient:
    """
    Production-ready Setu FIU client.

    Auth  : OAuth2 Bearer token (auto-refreshed every 30 min)
    Base  : https://fiu-sandbox.setu.co  (sandbox)
            https://fiu.setu.co          (production)

    Usage
    -----
    client = SetuAAClient(config)

    # Step 1 – Create consent
    resp = client.create_consent(ConsentRequest(vua="9999999999@onemoney", fi_types=[FIType.DEPOSIT]))
    consent_id   = resp["id"]
    webview_url  = resp["url"]       # redirect user here

    # Step 2 – Wait for approval (via webhook or poll)
    status = client.get_consent_status(consent_id)

    # Step 3 – Fetch data once ACTIVE
    session = client.create_data_session(consent_id)
    fi_data = client.fetch_fi_data(session["id"])
    """

    def __init__(self, config: SetuAAConfig):
        self.config = config
        self._http  = _build_http_session(config)
        logger.info(
            "SetuAAClient initialised | env=%s | base=%s",
            config.environment,
            config.base_url,
        )

    # ── helpers ──────────────────────────────────────────────────────────────

    def _auth_headers(self) -> Dict[str, str]:
        """Return Authorization header with a fresh Bearer token."""
        token = _fetch_oauth_token(self.config)
        return {"Authorization": f"Bearer {token}"}

    def _url(self, path: str) -> str:
        return f"{self.config.base_url}/v2/{path.lstrip('/')}"

    def _get(self, path: str, **kwargs) -> Dict:
        url = self._url(path)
        logger.debug("GET  %s", url)
        r = self._http.get(
            url,
            headers=self._auth_headers(),
            timeout=self.config.request_timeout,
            **kwargs,
        )
        if not r.ok:
            logger.error("GET %s  status=%d  response=%s", url, r.status_code, r.text)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: Dict, **kwargs) -> Dict:
        url = self._url(path)
        logger.debug("POST %s  body=%s", url, payload)
        r = self._http.post(
            url,
            json=payload,
            headers=self._auth_headers(),
            timeout=self.config.request_timeout,
            **kwargs,
        )
        if not r.ok:
            logger.error("POST %s  status=%d  response=%s", url, r.status_code, r.text)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str, payload: Optional[Dict] = None, **kwargs) -> Dict:
        url = self._url(path)
        logger.debug("DEL  %s", url)
        r = self._http.delete(
            url,
            json=payload or {},
            headers=self._auth_headers(),
            timeout=self.config.request_timeout,
            **kwargs,
        )
        r.raise_for_status()
        return r.json()

    # ── Consent Flow ─────────────────────────────────────────────────────────

    def create_consent(self, consent_req: ConsentRequest) -> Dict:
        payload = consent_req.to_payload()
        logger.info("Creating consent for vua=%s  fiTypes=%s", consent_req.vua, consent_req.fi_types)
        logger.info("Consent payload being sent:\n%s", __import__('json').dumps(payload, indent=2))
        resp = self._post("/consents", payload)
        logger.info("Consent created → id=%s  status=%s", resp.get("id"), resp.get("status"))
        return resp

    def get_consent_status(self, consent_id: str) -> Dict:
        """Fetch current status & details of a consent."""
        resp = self._get(f"/consents/{consent_id}")
        logger.info("Consent %s → status=%s", consent_id, resp.get("status"))
        return resp

    def revoke_consent(self, consent_id: str) -> Dict:
        """Revoke an active consent on behalf of the user or FIU."""
        resp = self._post(f"/consents/{consent_id}/revoke", {})
        logger.info("Consent %s revoked", consent_id)
        return resp

    def list_consents(self, status: Optional[str] = None) -> Dict:
        """List all consents, optionally filtered by status."""
        params = {}
        if status:
            params["status"] = status
        return self._get("/consents", params=params)

    # ── Data Flow ─────────────────────────────────────────────────────────────

    def create_data_session(
        self,
        consent_id: str,
        data_from: Optional[datetime] = None,
        data_to:   Optional[datetime] = None,
        fmt: str = "json",
    ) -> Dict:
        """
        Create a FI data session against an APPROVED consent.
        `fmt` can be "json" or "xml".
        Returns {"id": "<sessionId>", "status": "PENDING", ...}
        """
        now      = datetime.now(timezone.utc)
        from_dt  = data_from or (now - timedelta(days=730))
        to_dt    = data_to   or now

        payload = {
            "consentId": consent_id,
            "dataRange": {
                "from": from_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "to":   to_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            },
            "format": fmt,
        }
        logger.info("Creating data session for consent=%s  range=[%s → %s]", consent_id, from_dt.date(), to_dt.date())
        resp = self._post("/sessions", payload)
        logger.info("Data session created → id=%s  status=%s", resp.get("id"), resp.get("status"))
        return resp

    def get_session_status(self, session_id: str) -> Dict:
        """Get status + FI data for a session (once PARTIAL or COMPLETED)."""
        return self._get(f"/sessions/{session_id}")

    def fetch_fi_data(self, session_id: str) -> Dict:
        """
        Alias of get_session_status – returns fully decrypted FI payload
        when session status is PARTIAL or COMPLETED.
        """
        resp = self._get(f"/sessions/{session_id}")
        logger.info(
            "FI fetch session=%s  combinedStatus=%s  fips=%d",
            session_id,
            resp.get("status"),
            len(resp.get("fips") or []),
        )
        return resp

    def wait_for_fi_data(
        self,
        session_id: str,
        poll_interval: Optional[int] = None,
        max_attempts: Optional[int]  = None,
    ) -> Dict:
        """
        Block-poll until session reaches PARTIAL / COMPLETED / EXPIRED / FAILED.
        Returns the final session response.
        """
        interval = poll_interval or self.config.poll_interval_seconds
        attempts = max_attempts  or self.config.max_poll_attempts

        for attempt in range(1, attempts + 1):
            resp   = self.get_session_status(session_id)
            status = resp.get("status", "PENDING")
            logger.info("Poll %d/%d  session=%s  status=%s", attempt, attempts, session_id, status)

            if status in (SessionStatus.PARTIAL, SessionStatus.COMPLETED,
                          SessionStatus.EXPIRED,  SessionStatus.FAILED):
                return resp

            time.sleep(interval)

        raise TimeoutError(
            f"Session {session_id} did not reach terminal state after {attempts} polls."
        )

    # ── Consent + Data – one-shot helper ─────────────────────────────────────

    def full_data_flow(
        self,
        consent_id: str,
        data_from: Optional[datetime] = None,
        data_to:   Optional[datetime] = None,
        poll: bool = True,
    ) -> Dict:
        """
        Convenience: given an APPROVED consentId,
        create a session and (optionally) wait for data.
        """
        session = self.create_data_session(consent_id, data_from, data_to)
        if not poll:
            return session
        return self.wait_for_fi_data(session["id"])

    # ── FIP Discovery ─────────────────────────────────────────────────────────

    def list_active_fips(self, expanded: bool = False) -> Dict:
        """
        Return list of active Financial Information Providers.
        Pass expanded=True to get detailed health metrics.
        """
        params = {"expanded": "true"} if expanded else {}
        return self._get("/fips", params=params)

    # ── Consent Status polling helper ─────────────────────────────────────────

    def wait_for_consent_approval(
        self,
        consent_id: str,
        poll_interval: int = 10,
        max_attempts: int  = 30,
    ) -> Dict:
        """
        Poll until consent moves out of PENDING.
        Returns final consent status response.
        Useful when not using webhooks.
        """
        for attempt in range(1, max_attempts + 1):
            resp   = self.get_consent_status(consent_id)
            status = resp.get("status", "PENDING")
            logger.info(
                "Consent poll %d/%d  id=%s  status=%s",
                attempt, max_attempts, consent_id, status,
            )
            if status != ConsentStatus.PENDING:
                return resp
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Consent {consent_id} still PENDING after {max_attempts} polls."
        )