"""SchemeBook — independent South African medical scheme directory and
consumer jargon resource. ZA portfolio, under Sentrix Digital.

Data layer: no duplication. SchemeBook reuses cms_authority.py (the same
CMS-registered scheme / PMB / CDL / DTP data that Core ZA and ClinicalAtlas
ZA already ingest) — it is a standalone front door onto that data, not a
second copy of it. The one thing genuinely new here is the plain-language
jargon glossary, which is SchemeBook's own consumer-facing content.
"""

from __future__ import annotations

from typing import Any

from cms_authority import cms_data_sources, cms_stats

TITLE = "SchemeBook"
TAGLINE = (
    "An independent directory of South African private medical schemes, and a "
    "plain-language guide to the jargon and complexity of medical aid — built "
    "to be navigated by anyone: consumers working out their own cover, industry "
    "professionals, international bodies seeking to understand South Africa's "
    "system, and institutional reformists looking for one central place to "
    "start from."
)

JARGON: list[dict[str, str]] = [
    {
        "term": "Open scheme",
        "slug": "open-scheme",
        "one_liner": "Anyone can join, regardless of employer.",
        "detail": (
            "An open medical scheme accepts members from the public, not just "
            "employees of a particular company. Discovery Health, Bonitas, and "
            "Momentum Health are open schemes. Compare this with a restricted "
            "scheme, which only accepts members from a defined group."
        ),
    },
    {
        "term": "Restricted scheme",
        "slug": "restricted-scheme",
        "one_liner": "Membership is limited to a specific employer, industry, or profession.",
        "detail": (
            "A restricted scheme only accepts members who belong to a defined "
            "group — usually an employer, industry body, or profession (for "
            "example, a scheme for a specific bank's staff, or for civil "
            "servants). You generally cannot join one from outside that group."
        ),
    },
    {
        "term": "PMB (Prescribed Minimum Benefits)",
        "slug": "pmb",
        "one_liner": "A legally mandated minimum level of cover every scheme must provide.",
        "detail": (
            "By law, every South African medical scheme must cover a defined "
            "list of conditions and emergencies in full, regardless of which "
            "plan you're on — these are the Prescribed Minimum Benefits (PMBs). "
            "PMBs exist so that serious or life-threatening conditions aren't "
            "left uncovered because of plan limits or exclusions."
        ),
    },
    {
        "term": "CDL (Chronic Disease List)",
        "slug": "cdl",
        "one_liner": "The specific chronic conditions PMB cover extends to.",
        "detail": (
            "The Chronic Disease List names around two dozen chronic conditions "
            "— such as diabetes, asthma, and hypertension — that schemes must "
            "fund as part of PMB cover, including ongoing medication, according "
            "to a defined treatment algorithm (see DTP)."
        ),
    },
    {
        "term": "DTP (Diagnosis Treatment Pair)",
        "slug": "dtp",
        "one_liner": "The government-set minimum treatment standard for a CDL condition.",
        "detail": (
            "For each Chronic Disease List condition, a Diagnosis Treatment "
            "Pair sets out the diagnosis and the minimum standard of treatment "
            "a scheme must fund at PMB level — so 'PMB cover for diabetes' has "
            "a specific, checkable meaning rather than being left to the scheme's "
            "discretion."
        ),
    },
    {
        "term": "Co-payment",
        "slug": "co-payment",
        "one_liner": "An amount you pay yourself, on top of what the scheme pays.",
        "detail": (
            "Many plans require a co-payment for certain procedures or when you "
            "use a non-network provider — a fixed or percentage amount you're "
            "responsible for even though the claim is otherwise covered. PMB "
            "conditions treated at a designated service provider are generally "
            "protected from co-payments."
        ),
    },
    {
        "term": "Designated Service Provider (DSP)",
        "slug": "dsp",
        "one_liner": "The provider your scheme names as the no-extra-cost option.",
        "detail": (
            "A scheme can name specific hospitals, pharmacies, or doctor "
            "networks as its Designated Service Providers. Using a DSP for a "
            "PMB condition means you shouldn't face a co-payment; going outside "
            "the DSP network for a non-emergency generally means you will, "
            "unless no DSP is reasonably available."
        ),
    },
    {
        "term": "Waiting period",
        "slug": "waiting-period",
        "one_liner": "A window after joining where some or all benefits aren't payable yet.",
        "detail": (
            "Schemes may impose a general waiting period (up to 3 months) and/or "
            "a condition-specific waiting period (up to 12 months) when you join "
            "or upgrade, particularly if you weren't on another scheme "
            "immediately beforehand. PMB conditions cannot be excluded by a "
            "condition-specific waiting period, only delayed by the general one."
        ),
    },
    {
        "term": "Late-joiner penalty",
        "slug": "late-joiner-penalty",
        "one_liner": "A permanent extra premium loading for joining a scheme later in life.",
        "detail": (
            "If you join a medical scheme for the first time after age 35 "
            "without continuous prior cover, schemes may apply a late-joiner "
            "penalty — an extra percentage added to your premium, for as long "
            "as you remain a scheme member. It rewards continuous cover rather "
            "than only joining once you need it."
        ),
    },
    {
        "term": "Savings account / above-threshold benefit",
        "slug": "savings-account",
        "one_liner": "A day-to-day medical spending pot that isn't the same as your main cover.",
        "detail": (
            "Many plans allocate part of your premium to a personal medical "
            "savings account for day-to-day claims (GP visits, over-the-counter "
            "medicine). Once that's exhausted, some plans have an above-threshold "
            "benefit that kicks back in — but there's often a gap in between "
            "where you pay out of pocket."
        ),
    },
]


def data_sources() -> list[dict[str, str]]:
    """SchemeBook's ingestion sources — same registry as Core ZA's CMS layer,
    surfaced under SchemeBook's own name for the backend definition page."""
    return cms_data_sources()


def stats() -> dict[str, int]:
    return cms_stats()


def jargon_term(slug: str) -> dict[str, str] | None:
    return next((t for t in JARGON if t["slug"] == slug), None)


def context() -> dict[str, Any]:
    return {
        "title": TITLE,
        "tagline": TAGLINE,
        "stats": stats(),
        "jargon": JARGON,
    }
