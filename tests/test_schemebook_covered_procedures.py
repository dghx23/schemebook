"""Smoke tests for the independent SchemeBook site."""

import pytest

from app import app
from cms_authority import cms_stats


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize("path", [
    "/", "/explore", "/covered-procedures", "/public-care", "/cost-guide",
    "/jargon", "/jargon/open-scheme",
])
def test_public_pages_render_at_host_root(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"SchemeBook" in response.data


def test_covered_conditions_source_scope(client):
    response = client.get("/covered-procedures")
    body = response.get_data(as_text=True)
    assert "271 medical conditions" in body
    assert f"{cms_stats()['dtp_conditions']} DTP records currently indexed" in body
    assert "reconciled" in body


def test_covered_condition_search_and_detail(client):
    search = client.get("/covered-procedures?q=906A")
    assert search.status_code == 200
    assert b"Acute generalised paralysis" in search.data
    detail = client.get("/covered-procedures/906A")
    assert detail.status_code == 200
    assert b"Medical management; ventilation and plasmapheresis" in detail.data


def test_unknown_detail_is_not_silently_invented(client):
    assert client.get("/covered-procedures/no-such-code").status_code == 404
    assert client.get("/jargon/no-such-term").status_code == 404


def test_client_assets_are_served(client):
    for asset in ("styles.css", "core-za.js", "content.js", "guide.js", "app.js"):
        assert client.get("/static/schemebook/" + asset).status_code == 200
