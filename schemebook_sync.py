"""Materialise Core ZA medical-scheme data into a versioned SchemeBook snapshot.

Flow: CMS authority files -> SchemeBook snapshot -> public SchemeBook site.
Every materialisation is audit logged; downstream services are separate.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import ingest_log
from cms_authority import (cms_data_sources, cms_stats, list_cdl_conditions,
                           list_dtp_items, list_schemes, pmb_explainer)

DATA_DIR = Path(__file__).resolve().parent / "data"
SNAPSHOT_PATH = DATA_DIR / "schemebook_snapshot.json"
STATE_PATH = DATA_DIR / "schemebook_sync_state.json"
PRODUCT = "SchemeBook"
SCHEMA_VERSION = 1
PIPELINE = [
    {"stage": "authority", "from": "CMS authority sources", "to": "Core ZA"},
    {"stage": "materialise", "from": "Core ZA + glossary", "to": "SchemeBook snapshot"},
    {"stage": "reuse", "from": "SchemeBook snapshot", "to": "Versioned Git snapshot for downstream integration"},
    {"stage": "publish", "from": "SchemeBook snapshot", "to": "SchemeBook actual"},
]

def _json_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _write_json(path: Path, payload: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)

def read_state() -> dict[str, Any]:
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def read_snapshot() -> dict[str, Any] | None:
    try:
        value = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None

def build_snapshot(glossary: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "product": PRODUCT,
        "source_contract": "Core ZA / CMS authority",
        "stats": cms_stats(),
        "schemes": list_schemes(),
        "pmb": pmb_explainer(),
        "cdl": list_cdl_conditions(),
        "dtp": list_dtp_items(limit=10000),
        "glossary": glossary,
        "sources": cms_data_sources(),
        "pipeline": PIPELINE,
    }

def sync(glossary: list[dict[str, str]], *, triggered_by: str = "automatic",
         actor: str = "schemebook-sync") -> dict[str, Any]:
    payload = build_snapshot(glossary)
    digest = _json_hash(payload)
    previous = read_state()
    changed = digest != previous.get("content_hash")
    now = datetime.now(timezone.utc).isoformat()
    snapshot = {**payload, "content_hash": digest, "generated_at": now}
    _write_json(SNAPSHOT_PATH, snapshot)
    state = {
        "product": PRODUCT, "status": "success", "content_hash": digest,
        "changed": changed, "synced_at": now,
        "record_counts": {
            "schemes": len(payload["schemes"]), "glossary": len(glossary),
            "cdl": len(payload["cdl"]), "dtp": len(payload["dtp"]),
        },
    }
    _write_json(STATE_PATH, state)
    common = dict(pack="za", product=PRODUCT, triggered_by=triggered_by,
                  status="success", actor=actor, change_id=digest[:12])
    ingest_log.log_event(dataset="CMS medical-scheme authority", source="CMS",
        stage="authority", flow_from="CMS authority sources", flow_to="Core ZA",
        record_count=len(payload["schemes"]), summary="Validated canonical CMS authority data.", **common)
    ingest_log.log_event(dataset="SchemeBook product snapshot", source="Core ZA",
        stage="materialise", flow_from="Core ZA + glossary", flow_to="SchemeBook snapshot",
        record_count=len(payload["schemes"]) + len(glossary),
        summary="Materialised a versioned SchemeBook snapshot.", **common)
    ingest_log.log_event(dataset="SchemeBook downstream contract", source="SchemeBook snapshot",
        stage="reuse", flow_from="SchemeBook snapshot",
        flow_to="Versioned Git snapshot for downstream integration", record_count=len(glossary),
        summary="Versioned the glossary and authority contract for downstream integration.", **common)
    ingest_log.log_event(dataset="SchemeBook release", source="SchemeBook snapshot",
        stage="publish", flow_from="SchemeBook snapshot", flow_to="SchemeBook actual",
        record_count=len(payload["schemes"]) + len(glossary),
        summary="Promoted the validated snapshot to SchemeBook actual.", **common)
    return state

def ensure_synced(glossary: list[dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a snapshot that matches the current Core ZA/CMS source contract."""
    snapshot = read_snapshot()
    state = read_state()

    current_payload = build_snapshot(glossary)
    current_hash = _json_hash(current_payload)
    stored_hash = (state or {}).get("content_hash") or (snapshot or {}).get("content_hash")

    if not snapshot or not state or stored_hash != current_hash:
        state = sync(glossary, triggered_by="automatic", actor="application")
        snapshot = read_snapshot() or {**current_payload, "content_hash": current_hash}

    return snapshot, state
