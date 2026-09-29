#!/usr/bin/env python3
"""Run the complete SchemeBook authority-to-release synchronisation."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import schemebook
import schemebook_sync
from cms_authority import refresh_pmb_cache

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-authority", action="store_true")
    parser.add_argument("--trigger", default="scheduled")
    args = parser.parse_args()
    if args.refresh_authority:
        refresh_pmb_cache(force=True)
    state = schemebook_sync.sync(
        schemebook.JARGON, triggered_by=args.trigger, actor="github-actions"
    )
    counts = state["record_counts"]
    print(
        f"SchemeBook {state['content_hash'][:12]}: "
        f"{counts['schemes']} schemes, {counts['glossary']} terms, "
        f"{counts['cdl']} CDL, {counts['dtp']} DTP"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
