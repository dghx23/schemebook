"""Core ZA index of official South African public patient tariff publications.

The index records source documents, not parsed tariff rows or a patient quote.
Only the Department of Health and a public facility can confirm applicability.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import json

SOURCE_URL = "https://www.health.gov.za/uniform-patient-fee-schedule/"
_INDEX = Path(__file__).resolve().parent / "data" / "coreza" / "upfs_source_index.json"


def upfs_source_index() -> dict:
    """Read the reviewed snapshot; never silently substitute private scheme fees."""
    with _INDEX.open(encoding="utf-8") as handle:
        return json.load(handle)


def current_upfs_annexures(as_of: date | None = None) -> list[dict]:
    """Return latest published effective year no later than the requested day."""
    today = (as_of or date.today()).isoformat()
    rows = [row for row in upfs_source_index()["annexures"]
            if row["effective_from"] <= today]
    if not rows:
        return []
    latest = max(row["effective_from"] for row in rows)
    return [row for row in rows if row["effective_from"] == latest]


def source_registry_row() -> dict[str, str]:
    snapshot = upfs_source_index()
    return {
        "domain": "Public patient fees (ZA)",
        "domain_url": "core.za",
        "source": "National Department of Health — Uniform Patient Fee Schedule",
        "feed_type": "Official publication index (dated spreadsheet links)",
        "api_access": SOURCE_URL,
        "refresh": "Check the official publication page each April and on demand",
        "consumed_by": "Core ZA · SchemeBook public care and cost guide · ClinicalAtlas ZA context",
        "status": "Source index ingested as of " + snapshot["checked_at"]
                  + "; spreadsheet tariff rows not ingested",
    }
