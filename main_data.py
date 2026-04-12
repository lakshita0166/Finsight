"""
main_data.py – End-to-end demo for Setu Account Aggregator FIU integration.

Demonstrates:
  1.  List active FIPs
  2.  Create a consent (all major FI types)
  3.  Redirect URL printed → user approves on AA app
  4.  Poll for consent approval (sandbox: auto-approved)
  5.  Create a data session
  6.  Poll for FI data
  7.  Parse & display structured data

Sandbox test VUA : 9999999999@onemoney   (auto-approves consent)
                   9999999999@anumati
                   9999999999@finvu
Static OTP (Setu FIP-2): 123456

Run:
    python main_data.py
    python main_data.py --preset banking --vua 9999999999@onemoney
    python main_data.py --list-fips
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone, timedelta

from setu_aa_client import SetuAAClient, SetuAAConfig
from fi_presets import PRESETS, PRESET_BANKING
from fi_parser import parse_session_response, summarise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("setu_aa.demo")


# ─────────────────────────────────────────────────────────────────────────────
# YOUR CREDENTIALS  (sourced directly from your Bridge config)
# ─────────────────────────────────────────────────────────────────────────────
CONFIG = SetuAAConfig(
    client_id           = "ddd1cd58-afce-43b9-bcc9-ed10de775d3c",
    client_secret       = "JE6nZZH3wtfMX2BNPnxLOZ3bBWxAJfa0",
    product_instance_id = "cb266eb6-c770-4335-88f0-732fc391c58a",
    environment         = "sandbox",
    # Sandbox AA API  : https://fiu-sandbox.setu.co/v2/...
    # Sandbox Token   : https://uat.setu.co/api/v2/auth/token
    # Change environment to "production" when going live
    max_poll_attempts     = 20,
    poll_interval_seconds = 6,
)


# ─────────────────────────────────────────────────────────────────────────────
# Demo flows
# ─────────────────────────────────────────────────────────────────────────────

def demo_test_token(config: SetuAAConfig):
    """Step 0 – Verify credentials by fetching an OAuth token."""
    from setu_aa_client import _fetch_oauth_token
    print("\n" + "─"*60)
    print("  Step 0: Testing OAuth token generation")
    print(f"  Token URL : {config.token_url}")
    print(f"  Client ID : {config.client_id}")
    print("─"*60)
    try:
        token = _fetch_oauth_token(config)
        print(f"  ✅ Token OK → {token[:40]}…")
    except Exception as e:
        print(f"  ❌ Token FAILED → {e}")
        print("\n  Check your client_id and client_secret on bridge.setu.co")
        raise


def demo_list_fips(client: SetuAAClient):
    print("\n" + "─"*60)
    print("  Active FIPs")
    print("─"*60)
    resp = client.list_active_fips(expanded=False)
    fips = resp.get("fips") or resp.get("FIPs") or resp
    if isinstance(fips, list):
        for f in fips[:20]:   # cap display
            name   = f.get("name") or f.get("fipID") or f
            status = f.get("status", "ACTIVE")
            print(f"  {status:8s}  {name}")
    else:
        print(json.dumps(resp, indent=2))


def demo_consent_and_data(
    client: SetuAAClient,
    preset_name: str = "banking",
    vua: str = "9999999999@onemoney",
):
    print(f"\n{'─'*60}")
    print(f"  Flow: preset={preset_name}  vua={vua}")
    print("─"*60)

    # ── Step 1: Build & submit consent ────────────────────────────────────────
    preset_fn = PRESETS.get(preset_name)
    if not preset_fn:
        print(f"Unknown preset '{preset_name}'. Available: {list(PRESETS)}")
        sys.exit(1)

    consent_req = preset_fn(vua)
    consent_req.redirect_url = "https://setu.co"   # valid redirect URL

    print(f"\n[1/5] Creating consent for fiTypes={[f.value for f in consent_req.fi_types]}")
    consent_resp = client.create_consent(consent_req)
    consent_id   = consent_resp.get("id")
    webview_url  = consent_resp.get("url")

    print(f"      consent_id = {consent_id}")
    print(f"      status     = {consent_resp.get('status')}")
    print(f"\n      *** Redirect user to this URL to approve consent ***")
    print(f"      {webview_url}\n")

    # ── Step 2: Poll for approval ─────────────────────────────────────────────
    print("[2/5] Polling for consent approval (sandbox auto-approves after linking account)…")
    print("      (In production: redirect user to URL above and wait for webhook)")
    try:
        consent_status = client.wait_for_consent_approval(
            consent_id,
            poll_interval=8,
            max_attempts=25,
        )
        final_status = consent_status.get("status")
        print(f"      Consent final status = {final_status}")
    except TimeoutError:
        print("      ⚠️  Consent not approved within timeout.")
        print("         Please open the URL above in a browser, approve, then re-run.")
        print(f"         Alternatively, call:  client.full_data_flow('{consent_id}')")
        return

    if final_status != "ACTIVE":
        print(f"      ❌ Consent not active (status={final_status}). Cannot fetch data.")
        return

    # ── Step 3: Create data session ───────────────────────────────────────────
    print("\n[3/5] Creating data session…")

    # Use the dataRange from the original consent creation response — guaranteed valid
    # The session dataRange MUST be within (or equal to) the consent's approved FIDataRange
    consent_detail = consent_resp.get("detail", {})
    approved_range = consent_detail.get("dataRange", {})

    if approved_range.get("from") and approved_range.get("to"):
        data_from = datetime.fromisoformat(approved_range["from"].replace("Z", "+00:00"))
        data_to   = datetime.fromisoformat(approved_range["to"].replace("Z", "+00:00"))
        print(f"      Using consent's approved dataRange: {data_from.date()} → {data_to.date()}")
    else:
        # Last resort: re-fetch the consent to get the dataRange
        full_consent  = client.get_consent_status(consent_id)
        approved_range = full_consent.get("detail", {}).get("dataRange", {})
        if approved_range.get("from") and approved_range.get("to"):
            data_from = datetime.fromisoformat(approved_range["from"].replace("Z", "+00:00"))
            data_to   = datetime.fromisoformat(approved_range["to"].replace("Z", "+00:00"))
            print(f"      dataRange from re-fetch: {data_from.date()} → {data_to.date()}")
        else:
            # Absolute fallback — use the preset's dataRange values
            data_to   = datetime.now(timezone.utc)
            data_from = data_to - timedelta(days=730)
            print(f"      ⚠️  Using fallback dataRange: {data_from.date()} → {data_to.date()}")

    session = client.create_data_session(consent_id, data_from=data_from, data_to=data_to)
    session_id = session.get("id")
    print(f"      session_id = {session_id}  status={session.get('status')}")

    # ── Step 4: Poll for FI data ──────────────────────────────────────────────
    print("\n[4/5] Waiting for FI data…")
    fi_resp = client.wait_for_fi_data(session_id)
    print(f"      Combined session status = {fi_resp.get('status')}")

    # ── Step 5: Parse & display ───────────────────────────────────────────────
    print("\n[5/5] Parsing FI data…")
    parsed = parse_session_response(fi_resp)
    summarise(parsed)

    # Raw dump (optional)
    output_file = f"fi_data_{consent_id[:8]}.json"
    with open(output_file, "w") as fh:
        json.dump(fi_resp, fh, indent=2)
    print(f"  📄 Raw FI data saved to {output_file}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Setu AA Demo")
    parser.add_argument("--preset",    default="banking",
                        help="Preset name: " + " | ".join(PRESETS.keys()))
    parser.add_argument("--vua",       default="9999999999@onemoney",
                        help="Virtual User Address (e.g. 9999999999@onemoney)")
    parser.add_argument("--test-token", action="store_true",
                        help="Test OAuth token generation only and exit")
    parser.add_argument("--list-fips", action="store_true",
                        help="List active FIPs and exit")
    parser.add_argument("--session",   default="",
                        help="Fetch data for an existing session ID")
    parser.add_argument("--consent",   default="",
                        help="Create data session for an existing approved consent ID")
    args = parser.parse_args()

    if args.test_token:
        demo_test_token(CONFIG)
        return

    client = SetuAAClient(CONFIG)

    if args.list_fips:
        demo_list_fips(client)
        return

    if args.session:
        print(f"Fetching data for existing session: {args.session}")
        fi_resp = client.wait_for_fi_data(args.session)
        parsed  = parse_session_response(fi_resp)
        summarise(parsed)
        return

    if args.consent:
        print(f"Creating data session for approved consent: {args.consent}")
        fi_resp = client.full_data_flow(args.consent)
        parsed  = parse_session_response(fi_resp)
        summarise(parsed)
        return

    demo_consent_and_data(client, preset_name=args.preset, vua=args.vua)


if __name__ == "__main__":
    main()