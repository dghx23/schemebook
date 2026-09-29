"""Standalone SchemeBook ZA application served at the host root."""
from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, abort, render_template, request

import schemebook
from cms_authority import cms_stats, get_dtp, list_dtp_categories, list_dtp_items, list_schemes
from core_common_procedures import procedure_categories, procedure_concepts
from coreza_upfs import SOURCE_URL as UPFS_SOURCE_URL, current_upfs_annexures

app = Flask(__name__)
SNAPSHOT_PATH = Path(__file__).resolve().parent / "data/schemebook_snapshot.json"


@app.get("/health")
def health():
    return {"status": "ok", "service": "schemebook"}


@app.get("/")
def schemebook_home():
    try:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        snapshot = {}
    client_data = {
        "stats": cms_stats(),
        "schemes": list_schemes(),
        "glossary": schemebook.JARGON,
        "source_url": "https://www.medicalschemes.co.za/media-centre/the-medical-schemes-industry-in-2023/",
        "generated_at": snapshot.get("generated_at"),
        "content_hash": snapshot.get("content_hash"),
    }
    return render_template("schemebook/index.html", schemebook_client_data=client_data,
                           **schemebook.context())


@app.get("/explore")
def schemebook_explore():
    query = request.args.get("q", "").strip()[:100]
    needle = query.casefold()
    return render_template(
        "schemebook/explore.html", query=query, categories=procedure_categories(),
        procedures=procedure_concepts(query)[:80] if query else [],
        jargon=[term for term in schemebook.JARGON if needle in term["term"].casefold()
                or needle in term["one_liner"].casefold()][:30] if query else [],
    )


@app.get("/covered-procedures")
def schemebook_covered_procedures():
    query = request.args.get("q", "").strip()[:120]
    category_slug = request.args.get("category", "").strip()[:120]
    categories = list_dtp_categories()
    active_category = next((item["name"] for item in categories if item["slug"] == category_slug), None)
    items = list_dtp_items(category_slug=category_slug or None, query=query or None, limit=500) if query or category_slug else []
    return render_template("schemebook/covered_procedures.html", query=query,
                           category_slug=category_slug, active_category=active_category,
                           categories=categories, items=items,
                           total_indexed=cms_stats()["dtp_conditions"])


@app.get("/covered-procedures/<code>")
def schemebook_covered_procedure_detail(code: str):
    dtp = get_dtp(code)
    if not dtp:
        abort(404)
    return render_template("schemebook/covered_procedure_detail.html", dtp=dtp)


@app.get("/care-guide.html")
def care_guide_legacy():
    return schemebook_explore()


@app.get("/public-care")
def schemebook_public_care():
    return render_template("schemebook/public_care.html")


@app.get("/cost-guide")
def schemebook_cost_guide():
    return render_template("schemebook/cost_guide.html",
                           upfs_annexures=current_upfs_annexures(), upfs_source_url=UPFS_SOURCE_URL)


@app.get("/jargon")
def schemebook_jargon():
    return render_template("schemebook/jargon.html", jargon=schemebook.JARGON)


@app.get("/jargon/<slug>")
def schemebook_jargon_detail(slug: str):
    term = schemebook.jargon_term(slug)
    if not term:
        abort(404)
    return render_template("schemebook/jargon_detail.html", term=term, jargon=schemebook.JARGON)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
