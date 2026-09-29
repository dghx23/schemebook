"""Append-only, product-aware ingest and promotion audit log."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_PATH = Path(__file__).resolve().parent / "data" / "ingest_log.json"
MAX_ENTRIES = 2000

def _load() -> list[dict[str, Any]]:
    if not LOG_PATH.is_file():
        return []
    try:
        data = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []

def _save(entries: list[dict[str, Any]]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    target = entries[-MAX_ENTRIES:]
    temporary = LOG_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(target, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(LOG_PATH)

def log_event(*, pack: str, dataset: str, source: str = "", triggered_by: str,
              status: str, summary: str, actor: str | None = None,
              product: str = "", stage: str = "", flow_from: str = "",
              flow_to: str = "", record_count: int | None = None,
              change_id: str = "", details: dict[str, Any] | None = None) -> dict[str, Any]:
    """Record an ingest, materialisation, validation, or promotion event."""
    entries = _load()
    event = {
        "id": max((int(e.get("id", 0)) for e in entries), default=0) + 1,
        "pack": pack, "product": product, "dataset": dataset, "source": source,
        "stage": stage, "flow_from": flow_from, "flow_to": flow_to,
        "triggered_by": triggered_by, "status": status, "summary": summary,
        "record_count": record_count, "change_id": change_id,
        "details": details or {}, "actor": actor or "",
        "at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(event)
    _save(entries)
    return event

def recent_events(limit: int = 50, pack: str | None = None,
                  product: str | None = None) -> list[dict[str, Any]]:
    entries = _load()
    if pack:
        entries = [e for e in entries if e.get("pack") == pack]
    if product:
        entries = [e for e in entries if e.get("product") == product]
    return list(reversed(entries))[:limit]

def last_event_for(dataset: str, pack: str | None = None,
                   product: str | None = None) -> dict[str, Any] | None:
    for event in reversed(_load()):
        if event.get("dataset") != dataset:
            continue
        if pack is not None and event.get("pack") != pack:
            continue
        if product is not None and event.get("product") != product:
            continue
        return event
    return None

def failure_count(limit: int = 50, product: str | None = None) -> int:
    return sum(1 for event in recent_events(limit, product=product)
               if event.get("status") == "failed")
