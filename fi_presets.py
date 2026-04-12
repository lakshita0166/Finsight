"""
fi_presets.py – Pre-built ConsentRequest presets for every supported FI data type.

Rule: frequency.value must be 1 when fetchType=ONETIME
      frequency.value can be > 1 only when fetchType=PERIODIC
"""
from __future__ import annotations
from typing import Callable
from setu_aa_client import (
    ConsentRequest, FIType, ConsentMode, FetchType,
    ConsentType, DataLifeUnit, FrequencyUnit,
)


def PRESET_BANKING(vua: str) -> ConsentRequest:
    """Deposits – ONETIME fetch, frequency must be 1."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.DEPOSIT, FIType.TERM_DEPOSIT, FIType.RECURRING_DEPOSIT],
        purpose_code="101",
        purpose_text="Personal Finance / Income Verification",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_INVESTMENTS(vua: str) -> ConsentRequest:
    """Equities, MF, ETF, NPS, PPF, ULIP, INVIT, IDR – PERIODIC fetch."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.EQUITIES, FIType.MUTUAL_FUNDS, FIType.ETF,
                  FIType.NPS, FIType.PPF, FIType.ULIP, FIType.INVIT, FIType.IDR],
        purpose_code="101",
        purpose_text="Wealth Management",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.PERIODIC,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=6,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # once per month
        redirect_url="https://setu.co",
    )


def PRESET_CREDIT(vua: str) -> ConsentRequest:
    """Credit Cards and Loans – ONETIME."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.CREDIT_CARD, FIType.LOAN],
        purpose_code="103",
        purpose_text="Credit Underwriting",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_INSURANCE(vua: str) -> ConsentRequest:
    """Insurance Policies – ONETIME."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.INSURANCE_POLICIES],
        purpose_code="101",
        purpose_text="Insurance Portfolio Overview",
        consent_mode=ConsentMode.VIEW,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_GST(vua: str) -> ConsentRequest:
    """GST Returns – ONETIME."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.GST_GSTR1, FIType.GST_GSTR2A, FIType.GST_GSTR3B],
        purpose_code="101",
        purpose_text="GST Compliance & Revenue Assessment",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_EPFO_SIP_CIS(vua: str) -> ConsentRequest:
    """EPFO, SIP, CIS – PERIODIC."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.EPFO, FIType.SIP, FIType.CIS],
        purpose_code="101",
        purpose_text="Retirement & Savings Monitoring",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.PERIODIC,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=6,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=2,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # once per month
        redirect_url="https://setu.co",
    )


def PRESET_TAX(vua: str) -> ConsentRequest:
    """AIS + TIS – ONETIME."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.AIS, FIType.TIS],
        purpose_code="101",
        purpose_text="Tax Filing Assistance",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_NHB(vua: str) -> ConsentRequest:
    """NHB Statements – ONETIME."""
    return ConsentRequest(
        vua=vua,
        fi_types=[FIType.NHB_STATEMENTS],
        purpose_code="101",
        purpose_text="Home Loan & Housing Finance Assessment",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.ONE_TIME,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="MONTH",
        consent_duration_value=4,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=1,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # ONETIME → must be 1
        redirect_url="https://setu.co",
    )


def PRESET_ALL_DATA(vua: str) -> ConsentRequest:
    """Master preset – all 23 FI types, PERIODIC."""
    return ConsentRequest(
        vua=vua,
        fi_types=list(FIType),
        purpose_code="101",
        purpose_text="Comprehensive Financial Profile",
        consent_mode=ConsentMode.STORE,
        fetch_type=FetchType.PERIODIC,
        consent_types=[ConsentType.PROFILE, ConsentType.SUMMARY, ConsentType.TRANSACTIONS],
        consent_duration_unit="YEAR",
        consent_duration_value=1,
        data_life_unit=DataLifeUnit.YEAR,
        data_life_value=2,
        frequency_unit=FrequencyUnit.MONTH,
        frequency_value=1,          # once per month
        redirect_url="https://setu.co",
    )


PRESETS: dict[str, Callable[[str], ConsentRequest]] = {
    "banking":     PRESET_BANKING,
    "investments": PRESET_INVESTMENTS,
    "credit":      PRESET_CREDIT,
    "insurance":   PRESET_INSURANCE,
    "gst":         PRESET_GST,
    "epfo_sip":    PRESET_EPFO_SIP_CIS,
    "tax":         PRESET_TAX,
    "nhb":         PRESET_NHB,
    "all":         PRESET_ALL_DATA,
}