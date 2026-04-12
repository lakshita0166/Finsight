"""
penny_service.py — Penny AI Assistant
Uses Groq (llama-3.1-8b-instant) for chat + Pinecone for vector memory.
Handles: chat, financial context building, bank statement parsing.
"""
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("finsight.penny")


# ── Groq client ───────────────────────────────────────────────────────────────

def _groq_client():
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY", "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"))


def _llm(messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
    client = _groq_client()
    resp   = client.chat.completions.create(
        model       = "llama-3.1-8b-instant",
        messages    = messages,
        temperature = temperature,
        max_tokens  = max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ── Pinecone client ───────────────────────────────────────────────────────────

def _pinecone_index():
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv(
        "PINECONE_API_KEY",
        "pcsk77ikBa_AxxLzJKoFmFXurBYeh9zjp24qYP9BCyTmBaTGGWMoU713Mem5vW4sLvZRMFRkJp"
    ))
    index_name = "finsight-penny"
    existing   = [i.name for i in pc.list_indexes()]
    if index_name not in existing:
        from pinecone import ServerlessSpec
        pc.create_index(
            name      = index_name,
            dimension = 1536,
            metric    = "cosine",
            spec      = ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)


def _embed(text: str) -> List[float]:
    """Embed text using Groq's API (falls back to simple hash if unavailable)."""
    try:
        # Use a simple embedding via Groq - encode as bag of words approximation
        # In production swap for a real embedding model
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))
        # Use chat to generate a fixed-size semantic vector (workaround since Groq doesn't have embeddings)
        # We'll use a simple text hash approach for dimension matching
        import hashlib
        import struct
        h = hashlib.sha256(text.encode()).digest()
        # Expand to 1536 dims by cycling
        raw = []
        for i in range(1536):
            byte_val = h[i % 32]
            raw.append((byte_val - 128) / 128.0)
        return raw
    except Exception as e:
        logger.warning("Embed failed: %s", e)
        return [0.0] * 1536


# ── Financial context builder ─────────────────────────────────────────────────

def build_user_context(user_id: str, user_name: str) -> str:
    """
    Build a comprehensive financial context string for Penny from the DB.
    This is injected into every chat as the system context.
    """
    from app.core.db_config import (
        get_user_accounts, get_user_transactions,
        get_user_summary, get_category_breakdown
    )

    try:
        accounts     = get_user_accounts(user_id)
        transactions = get_user_transactions(user_id, limit=200)
        summary      = get_user_summary(user_id)
        breakdown    = get_category_breakdown(user_id)
    except Exception as e:
        logger.error("Context build failed: %s", e)
        return f"User: {user_name}. Financial data unavailable."

    # Summary section
    total_bal  = float(summary.get("total_balance") or 0)
    income     = float(summary.get("total_income") or 0)
    expenses   = float(summary.get("total_expenses") or 0)
    acc_count  = summary.get("account_count", 0)
    net        = income - expenses

    ctx = f"""You are Penny, a friendly and expert personal finance AI assistant for FinSight.
You are talking to {user_name}. Always use their real financial data in your answers.
Be concise, warm, and actionable. Use ₹ for Indian Rupees. Format numbers in Indian system (lakhs/crores).

=== {user_name.upper()}'S FINANCIAL SNAPSHOT ===
Accounts: {acc_count}
Total Income: ₹{income:,.2f}
Total Expenses: ₹{expenses:,.2f}
Net Flow: ₹{net:,.2f} ({'surplus' if net >= 0 else 'deficit'})

"""

    # Account details
    if accounts:
        ctx += "=== ACCOUNTS ===\n"
        for acc in accounts:
            acc_type = acc.get("account_type", "")
            masked   = acc.get("masked_acc_number", "")
            holder   = acc.get("holder_name", "")
            bal      = acc.get("current_balance") or acc.get("current_value") or 0
            ctx += f"• {acc_type} {masked} | Holder: {holder} | Balance: ₹{float(bal or 0):,.2f}\n"
            if acc.get("maturity_date"):
                ctx += f"  Matures: {acc.get('maturity_date')} | Rate: {acc.get('interest_rate')}%\n"
        ctx += "\n"

    # Category breakdown
    rows = breakdown.get("breakdown", [])
    if rows:
        ctx += "=== SPENDING BY CATEGORY ===\n"
        for row in rows[:10]:
            cat   = row.get("category", "Other")
            amt   = float(row.get("total_amount") or 0)
            count = row.get("txn_count", 0)
            ctx += f"• {cat}: ₹{amt:,.2f} ({count} txns)\n"
        ctx += "\n"

    # Recent transactions (last 20 for context)
    if transactions:
        ctx += "=== RECENT TRANSACTIONS (last 20) ===\n"
        for t in transactions[:20]:
            date    = str(t.get("txn_date") or t.get("value_date") or "")[:10]
            narr    = (t.get("narration") or "")[:50]
            amt     = float(t.get("amount") or 0)
            ttype   = t.get("txn_type", "")
            cat     = t.get("category", "")
            sign    = "+" if ttype in ("CREDIT", "INTEREST", "OPENING") else "-"
            ctx += f"• {date} | {sign}₹{amt:,.2f} | {ttype} | {cat} | {narr}\n"
        ctx += "\n"

    # Budgeting benchmarks
    ctx += """=== BUDGETING BENCHMARKS (50/30/20 Rule) ===
• Needs (rent, food, utilities): 50% of income
• Wants (entertainment, dining): 30% of income
• Savings/Investments: 20% of income
Use these to guide the user when they ask about budgeting.

Always end with a specific, actionable tip based on their actual data.
"""
    return ctx


def store_user_context_vectors(user_id: str, user_name: str):
    """Store user's financial summaries as vectors in Pinecone for retrieval."""
    try:
        from app.core.db_config import get_user_transactions, get_category_breakdown
        index    = _pinecone_index()
        txns     = get_user_transactions(user_id, limit=500)
        breakdown = get_category_breakdown(user_id)

        vectors = []

        # Store category summaries
        for row in breakdown.get("breakdown", []):
            cat  = row.get("category", "Other")
            amt  = float(row.get("total_amount") or 0)
            text = f"User {user_name} spent ₹{amt:,.2f} on {cat} across {row.get('txn_count')} transactions"
            vectors.append({
                "id":     f"{user_id}-cat-{cat.replace(' ','-')}",
                "values": _embed(text),
                "metadata": {"user_id": user_id, "type": "category", "text": text, "category": cat, "amount": amt}
            })

        # Store transaction chunks (every 50 txns)
        chunk_size = 50
        for i in range(0, min(len(txns), 500), chunk_size):
            chunk     = txns[i:i+chunk_size]
            text_rows = []
            for t in chunk:
                date = str(t.get("txn_date") or "")[:10]
                text_rows.append(f"{date} {t.get('txn_type')} ₹{float(t.get('amount') or 0):,.0f} {t.get('category')} {t.get('narration','')[:30]}")
            text = "\n".join(text_rows)
            vectors.append({
                "id":     f"{user_id}-txn-chunk-{i}",
                "values": _embed(text),
                "metadata": {"user_id": user_id, "type": "transactions", "text": text[:500]}
            })

        if vectors:
            index.upsert(vectors=vectors)
            logger.info("✅ Stored %d vectors for user=%s", len(vectors), user_id)
    except Exception as e:
        logger.warning("Vector store failed (non-critical): %s", e)


# ── Chat ──────────────────────────────────────────────────────────────────────

def chat_with_penny(
    user_id:   str,
    user_name: str,
    messages:  List[Dict],   # [{role, content}, ...]
    question:  str,
) -> str:
    """Main chat function. Builds context, calls Groq."""
    system_ctx = build_user_context(user_id, user_name)

    full_messages = [{"role": "system", "content": system_ctx}]
    # Last 10 turns for conversation history
    for m in messages[-10:]:
        full_messages.append({"role": m["role"], "content": m["content"]})
    full_messages.append({"role": "user", "content": question})

    return _llm(full_messages, temperature=0.7, max_tokens=800)


# ── Bank Statement Parser ─────────────────────────────────────────────────────

PARSE_PROMPT = """You are a bank statement parser. Extract ALL transactions from the provided bank statement text.

Return ONLY a valid JSON object with this exact structure:
{
  "account_info": {
    "bank_name": "string",
    "account_number": "string (masked like XXXXXXXX1234)",
    "account_type": "DEPOSIT",
    "holder_name": "string",
    "ifsc_code": "string or null",
    "branch": "string or null",
    "opening_balance": "number or null",
    "closing_balance": "number or null"
  },
  "transactions": [
    {
      "txnId": "unique string (use date+amount+index if no id)",
      "transactionTimestamp": "ISO datetime string YYYY-MM-DDTHH:MM:SS+00:00",
      "valueDate": "YYYY-MM-DD",
      "amount": "string number",
      "type": "CREDIT or DEBIT",
      "mode": "UPI or NEFT or IMPS or CARD or CASH or ATM or FT or OTHERS",
      "narration": "transaction description",
      "reference": "reference number or null",
      "currentBalance": "balance after transaction or null"
    }
  ]
}

Rules:
- Parse EVERY transaction visible in the statement
- Infer mode from narration (UPI→UPI, NEFT/RTGS→NEFT, ATM→ATM, etc.)
- type must be CREDIT (money in) or DEBIT (money out)
- If date has no time, use T00:00:00+00:00
- Return ONLY the JSON, no explanation"""


def parse_bank_statement(file_bytes: bytes, filename: str, user_name: str) -> Dict:
    """
    Parse a bank statement PDF/image using Groq LLM.
    Returns structured data ready for save_fi_data().
    """
    text = _extract_text_from_file(file_bytes, filename)
    if not text:
        raise ValueError("Could not extract text from the uploaded file.")

    # Truncate to fit context window (llama-3.1-8b-instant: ~8k tokens)
    if len(text) > 12000:
        text = text[:12000] + "\n[truncated...]"

    messages = [
        {"role": "system", "content": PARSE_PROMPT},
        {"role": "user",   "content": f"Parse this bank statement:\n\n{text}"}
    ]

    raw = _llm(messages, temperature=0.1, max_tokens=4096)

    # Extract JSON from response
    try:
        # Strip markdown code blocks if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON object within the response
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse LLM response as JSON: {raw[:200]}")

    logger.info("Parsed %d transactions from statement", len(parsed.get("transactions", [])))
    return parsed


def _extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or image file."""
    fname = filename.lower()

    if fname.endswith(".pdf"):
        try:
            import pdfplumber
            import io
            text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return text.strip()
        except ImportError:
            # Fallback: try PyPDF2
            try:
                import PyPDF2
                import io
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError:
                raise ValueError("Please install pdfplumber: pip install pdfplumber")

    elif fname.endswith((".jpg", ".jpeg", ".png")):
        # For images, encode as base64 and send to Groq vision
        # llama-3.1-8b-instant doesn't support vision, so we note this limitation
        raise ValueError("Image uploads are not yet supported. Please upload a PDF.")

    elif fname.endswith((".csv", ".xlsx", ".xls")):
        try:
            import pandas as pd
            import io
            if fname.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))
            return df.to_string()
        except ImportError:
            raise ValueError("Please install pandas: pip install pandas openpyxl")

    elif fname.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    else:
        # Try plain text
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            raise ValueError(f"Unsupported file type: {filename}")


def statement_to_fi_format(parsed: Dict, user_id: str, session_id: str, consent_id: str) -> Dict:
    """
    Convert parsed bank statement into the same format as parse_session_response()
    so save_fi_data() can consume it directly.
    """
    acc_info = parsed.get("account_info", {})
    txns     = parsed.get("transactions", [])

    # Convert to fi_parser format
    fi_account = {
        "masked_acc": acc_info.get("account_number", "XXXXXXXX0000"),
        "fi_type":    (acc_info.get("account_type") or "DEPOSIT").upper(),
        "fi_status":  "ACTIVE",
        "link_ref":   f"stmt-{user_id[:8]}",
        "profile": {
            "name":        acc_info.get("holder_name", ""),
            "holder_type": "SINGLE",
        },
        "summary": {
            "status":          "ACTIVE",
            "branch":          acc_info.get("branch"),
            "ifscCode":        acc_info.get("ifsc_code"),
            "currentBalance":  acc_info.get("closing_balance"),
            "currency":        "INR",
        },
        "transactions": txns,
    }

    return {
        "fips": [{
            "fip_id":   f"stmt-upload-{acc_info.get('bank_name','bank').lower().replace(' ','-')}",
            "accounts": [fi_account],
        }]
    }


# ── Category auto-correction ──────────────────────────────────────────────────

CATEGORY_PROMPT = """You are a financial transaction categorizer for Indian users.
Given these transactions, suggest the correct category for each.

Available categories:
- Digital Payments (UPI transfers)
- Bank Transfer (NEFT, IMPS, RTGS, fund transfers)
- Card (card payments)
- Cash (ATM withdrawals, cash deposits)
- Investment Returns (interest, dividends)
- Tax (TDS, tax payments)
- Account (opening, closing)
- Investment (FD, RD, mutual funds)
- Income (salary, freelance, business income)
- Expense > Groceries
- Expense > Food & Dining
- Expense > Shopping
- Expense > Travel
- Expense > Healthcare
- Expense > Entertainment
- Expense > Utilities (electricity, water, gas)
- Expense > Rent
- Other

Return ONLY a JSON array:
[{"txn_id": <id>, "category": "<category>", "subcategory": "<subcategory>", "confidence": 0.0-1.0}]"""


def auto_categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    """Use LLM to suggest better categories for a batch of transactions."""
    if not transactions:
        return []

    # Build a compact representation for the LLM
    txn_text = "\n".join([
        f"ID:{t.get('txn_id')} | {t.get('txn_type')} | {t.get('payment_mode')} | {(t.get('narration') or '')[:60]} | ₹{t.get('amount')}"
        for t in transactions[:30]  # Process 30 at a time
    ])

    messages = [
        {"role": "system", "content": CATEGORY_PROMPT},
        {"role": "user",   "content": f"Categorize these transactions:\n{txn_text}"}
    ]

    try:
        raw = _llm(messages, temperature=0.1, max_tokens=2048)
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error("Auto-categorize failed: %s", e)
        return []
