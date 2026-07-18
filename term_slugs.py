"""Shared slug helpers for resource term drill-down."""

from __future__ import annotations

import re


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[/\\()]+", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")