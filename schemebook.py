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


# Additional plain-language terms are kept in the same canonical product module
# so the Site, Library wiki, and materialised copy all consume one definition.
JARGON.extend([
    {"term": "Medical scheme", "slug": "medical-scheme", "one_liner": "A regulated, member-funded pool that pays healthcare benefits under registered rules.", "detail": "The scheme collects contributions and funds benefits. It is overseen by the Council for Medical Schemes and differs from short-term medical insurance."},
    {"term": "Medical aid", "slug": "medical-aid", "one_liner": "The everyday South African name commonly used for medical scheme cover.", "detail": "The regulated entity is a medical scheme; the plan selected inside it is a benefit option."},
    {"term": "Medical insurance", "slug": "medical-insurance", "one_liner": "An insurance policy that pays stated amounts for specified health events.", "detail": "It commonly pays a fixed cash benefit and does not carry the same Prescribed Minimum Benefit duties as a medical scheme."},
    {"term": "Benefit option", "slug": "benefit-option", "one_liner": "The specific plan selected inside a medical scheme.", "detail": "Options differ in networks, day-to-day benefits, co-payments, limits and contributions."},
    {"term": "Principal member", "slug": "principal-member", "one_liner": "The person in whose name the membership is registered.", "detail": "Eligible family members may be registered as dependants under the principal member."},
    {"term": "Dependant", "slug": "dependant", "one_liner": "An eligible person covered under the principal membership.", "detail": "Adult and child dependant rates can differ, and proof of relationship or dependency may be required."},
    {"term": "Contribution", "slug": "contribution", "one_liner": "The regular amount paid to keep membership active.", "detail": "It is the monthly price for the selected option and covered members; it is not a co-payment."},
    {"term": "Underwriting", "slug": "underwriting", "one_liner": "The limited membership conditions a scheme may assess when someone joins.", "detail": "Depending on age and previous cover, lawful underwriting can include waiting periods or a late-joiner penalty."},
    {"term": "Condition-specific waiting period", "slug": "condition-specific-waiting-period", "one_liner": "A temporary restriction on claims linked to a pre-existing condition.", "detail": "A scheme may apply up to 12 months where permitted. Previous membership history affects what may lawfully be imposed."},
    {"term": "Emergency medical condition", "slug": "emergency-medical-condition", "one_liner": "A sudden condition needing immediate care to prevent serious harm.", "detail": "It is a PMB category. Clinical facts determine whether an event qualifies; contact the scheme as soon as reasonably possible."},
    {"term": "Medical savings account", "slug": "medical-savings-account", "one_liner": "Part of a contribution set aside for eligible day-to-day claims.", "detail": "It is the member's allocated pool, not an extra scheme benefit. PMB treatment may not be funded from savings."},
    {"term": "Self-payment gap", "slug": "self-payment-gap", "one_liner": "A period when savings are finished and the member funds day-to-day costs.", "detail": "On some options, qualifying expenses paid in this gap count toward an annual threshold."},
    {"term": "Benefit limit", "slug": "benefit-limit", "one_liner": "The most an option will pay for a defined benefit in a period.", "detail": "A limit can be an amount, number of visits or another cap. It cannot remove a valid PMB entitlement."},
    {"term": "Scheme tariff or rate", "slug": "scheme-tariff-rate", "one_liner": "The price level an option uses to calculate payment.", "detail": "If a provider charges more than the scheme rate, the member may owe the difference unless another protection applies."},
    {"term": "Out-of-pocket payment", "slug": "out-of-pocket-payment", "one_liner": "Any healthcare cost paid by the member and not reimbursed.", "detail": "This can include co-payments, tariff shortfalls, exclusions, costs above limits and self-payment-gap expenses."},
    {"term": "Provider network", "slug": "provider-network", "one_liner": "A group of healthcare providers contracted for an option or benefit.", "detail": "Confirm that both the facility and treating professional are in-network before planned care."},
    {"term": "Formulary", "slug": "formulary", "one_liner": "The list of medicines a scheme approves for a benefit.", "detail": "If a listed medicine is ineffective or harmful, a clinician can motivate for an alternative through the exception process."},
    {"term": "Generic medicine", "slug": "generic-medicine", "one_liner": "A medicine with the same active ingredient as an original brand product.", "detail": "Schemes may prefer registered generics to manage cost. Discuss substitution concerns with a pharmacist or clinician."},
    {"term": "Clinical protocol", "slug": "clinical-protocol", "one_liner": "The evidence-based steps used to decide how a condition should be treated.", "detail": "Protocols can set tests, medicines, referrals or stages. A clinician can motivate when the standard route is unsuitable."},
    {"term": "Pre-authorisation", "slug": "pre-authorisation", "one_liner": "Approval requested before planned treatment or admission.", "detail": "It is not an unlimited promise to pay: codes, providers, tariffs, limits and clinical changes can still affect the claim."},
    {"term": "Managed care", "slug": "managed-care", "one_liner": "Programmes that coordinate treatment and apply clinical funding rules.", "detail": "This includes chronic registration, case management, hospital authorisation and treatment protocols."},
    {"term": "Claim statement", "slug": "claim-statement", "one_liner": "The scheme's record of how it processed a claim.", "detail": "Compare the amount charged, scheme tariff, payment, reason code and member liability with the provider invoice."},
    {"term": "Tariff shortfall", "slug": "tariff-shortfall", "one_liner": "The difference between the provider's charge and the scheme payment.", "detail": "It differs from a fixed co-payment. Ask the provider and scheme for their written calculations."},
    {"term": "Claim rejection", "slug": "claim-rejection", "one_liner": "A decision not to pay all or part of a claim.", "detail": "Ask for the exact reason, code and registered rule in writing before deciding whether to correct, motivate or dispute it."},
    {"term": "Clinical motivation", "slug": "clinical-motivation", "one_liner": "Information from a clinician explaining why care is medically necessary.", "detail": "It should address diagnosis, relevant history, treatment tried, clinical risk and the requested service."},
    {"term": "Internal appeal", "slug": "internal-appeal", "one_liner": "A request for the scheme to reconsider its own decision.", "detail": "State the decision, desired outcome and relevant rule or PMB, and attach supporting evidence."},
    {"term": "CMS complaint", "slug": "cms-complaint", "one_liner": "A formal complaint to the Council for Medical Schemes.", "detail": "Use current CMS complaint guidance and include the scheme's correspondence and reference numbers."},
    {"term": "Registered scheme rules", "slug": "registered-scheme-rules", "one_liner": "The legally registered terms governing membership and benefits.", "detail": "Marketing summaries help, but registered rules and approved benefit schedules control how the option works."},
])


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
