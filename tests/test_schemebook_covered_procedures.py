"""SchemeBook covered PMB condition / DTP catalogue."""

from __future__ import annotations

import os

os.environ.setdefault("SITE_AUTH_DISABLED", "1")
os.environ.setdefault("PRODUCT_GATE_DISABLED", "1")

from app import app


def test_schemebook_covered_procedures_discloses_271_source_and_270_indexed():
    app.config["TESTING"] = True
    c = app.test_client()

    response = c.get(
        "/covered-procedures",
        headers={"Host": "riskatlas-0iob.onrender.com"},
    )
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Find a PMB condition or minimum treatment" in body
    assert "271 medical conditions" in body
    assert "270" in body
    assert "reconciled" in body


def test_schemebook_covered_procedures_search_and_detail():
    app.config["TESTING"] = True
    c = app.test_client()

    search = c.get(
        "/covered-procedures?q=906A",
        headers={"Host": "riskatlas-0iob.onrender.com"},
    )
    assert search.status_code == 200
    body = search.get_data(as_text=True)
    assert "906A" in body
    assert "Acute generalised paralysis" in body

    detail = c.get(
        "/covered-procedures/906A",
        headers={"Host": "riskatlas-0iob.onrender.com"},
    )
    assert detail.status_code == 200
    detail_body = detail.get_data(as_text=True)
    assert "Acute generalised paralysis" in detail_body
    assert "Medical management; ventilation and plasmapheresis" in detail_body
    assert "What it does not settle on its own" in detail_body


def test_schemebook_covered_procedures_redirects_off_product_host():
    app.config["TESTING"] = True
    c = app.test_client()

    response = c.get(
        "/covered-procedures",
        headers={"Host": "sentrixdigital.com"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "https://schemebook.riskatlas.co.za/covered-procedures"
