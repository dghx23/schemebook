"""CMS medical schemes & Prescribed Minimum Benefits — cached authority data for ClaimBuddy."""

from __future__ import annotations

import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from term_slugs import slugify

DATA_DIR = Path(__file__).resolve().parent / "data"
SCHEMES_PATH = DATA_DIR / "cms_schemes.json"
DTP_PATH = DATA_DIR / "cms_pmb_dtp.json"
PMB_HTML_PATH = DATA_DIR / "cms_pmb_raw.html"
PMB_CACHE_PATH = DATA_DIR / "cms_pmb_cache.json"

CMS_PMB_URL = "https://www.medicalschemes.co.za/resources/pmb/"
CMS_USER_AGENT = "ClaimBuddy/1.0 (+https://claimbuddy.co.za)"
CACHE_TTL_SECONDS = 86400  # daily refresh for PMB HTML

CMS_TITLE = "Medical schemes & PMBs"
CMS_TAGLINE = (
    "CMS-registered schemes, Prescribed Minimum Benefits (PMBs), Chronic Disease List, "
    "and Diagnosis Treatment Pairs — for income-protection context alongside Clinical Atlas."
)

CDL_CONDITIONS: list[dict[str, Any]] = [
    {
        "name": "Chronic renal disease",
        "acronym": "CRF",
        "atlas_slug": "chronic-kidney-disease",
        "category": "Renal",
        "claim_note": "PMB chronic cover may run parallel to disability cover — document renal staging and work limits.",
    },
    {
        "name": "Addison's disease",
        "acronym": "ADS",
        "atlas_slug": "addison-disease",
        "category": "Endocrine",
        "claim_note": "Steroid dependence and crisis risk — note sick leave and safety-critical duties.",
    },
    {
        "name": "Asthma",
        "acronym": "AST",
        "atlas_slug": "asthma",
        "category": "Respiratory",
        "claim_note": "PMB algorithms set minimum care — pair with material duty limits if exertion triggers symptoms.",
    },
    {
        "name": "Bronchiectasis",
        "acronym": "BCE",
        "atlas_slug": "bronchiectasis",
        "category": "Respiratory",
        "claim_note": "Chronic infection and fatigue — document stamina and attendance impact.",
    },
    {
        "name": "Cardiac failure",
        "acronym": "CHF",
        "atlas_slug": "heart-failure",
        "category": "Cardiovascular",
        "claim_note": "NYHA class and exertional limits matter for own-occupation and safety-critical tests.",
    },
    {
        "name": "Cardiomyopathy",
        "acronym": "CMY",
        "atlas_slug": "cardiomyopathy",
        "category": "Cardiovascular",
        "claim_note": "Arrhythmia and pump failure risk — capture specialist plan and duty restrictions.",
    },
    {
        "name": "Chronic obstructive pulmonary disorder",
        "acronym": "COP",
        "atlas_slug": "copd",
        "category": "Respiratory",
        "claim_note": "Progressive breathlessness — link spirometry and functional capacity to material duties.",
    },
    {
        "name": "Coronary artery disease",
        "acronym": "IHD",
        "atlas_slug": "coronary-artery-disease",
        "category": "Cardiovascular",
        "claim_note": "Angina and intervention history — note driving, shift work, and stress tolerance.",
    },
    {
        "name": "Crohn's disease",
        "acronym": "CSD",
        "atlas_slug": "crohn-disease",
        "category": "GI",
        "claim_note": "Flare frequency and toilet access — material for attendance and client-facing roles.",
    },
    {
        "name": "Diabetes insipidus",
        "acronym": "DBI",
        "atlas_slug": "diabetes-insipidus",
        "category": "Endocrine",
        "claim_note": "Fluid balance and monitoring — document travel and shift constraints.",
    },
    {
        "name": "Diabetes mellitus types 1 & 2",
        "acronym": "DM1/DM2",
        "atlas_slug": "type-2-diabetes-mellitus",
        "category": "Metabolic",
        "claim_note": "Hypoglycaemia and complications — HbA1c monitoring is a PMB algorithm benchmark.",
    },
    {
        "name": "Dysrhythmias",
        "acronym": "DYS",
        "atlas_slug": "atrial-fibrillation",
        "category": "Cardiovascular",
        "claim_note": "Palpitations and anticoagulation — safety-critical work may need explicit limits.",
    },
    {
        "name": "Epilepsy",
        "acronym": "EPL",
        "atlas_slug": "epilepsy-unspecified",
        "category": "Neurological",
        "claim_note": "Seizure control and driving licence rules — central to disability and safety assessments.",
    },
    {
        "name": "Bipolar mood disorder",
        "acronym": "BMD",
        "atlas_slug": "bipolar-affective-disorder",
        "category": "Mental health",
        "claim_note": "Episode frequency and cognition — separate PMB mental health cover from IP own-occupation test.",
    },
    {
        "name": "Hypothyroidism",
        "acronym": "TDH",
        "atlas_slug": "hypothyroidism",
        "category": "Metabolic",
        "claim_note": "Fatigue and cognition on suboptimal replacement — TSH monitoring is PMB-aligned.",
    },
    {
        "name": "Hypertension",
        "acronym": "HYP",
        "atlas_slug": "hypertension",
        "category": "Cardiovascular",
        "claim_note": "Controlled vs uncontrolled BP — document complications, not only script strength.",
    },
    {
        "name": "Glaucoma",
        "acronym": "GLC",
        "atlas_slug": "glaucoma",
        "category": "Ophthalmology",
        "claim_note": "Visual field loss — pair with driving, screen work, and safety-critical roles.",
    },
    {
        "name": "Haemophilia",
        "acronym": "HAE",
        "atlas_slug": "haemophilia",
        "category": "Haematology",
        "claim_note": "Bleeding risk and factor prophylaxis — manual and physical duties need explicit limits.",
    },
    {
        "name": "Ulcerative colitis",
        "acronym": "IBD",
        "atlas_slug": "ulcerative-colitis",
        "category": "GI",
        "claim_note": "Flare pattern and surgery history — attendance and travel impact for claims.",
    },
    {
        "name": "Systemic lupus erythematosus",
        "acronym": "SLE",
        "atlas_slug": "systemic-lupus-erythematosus",
        "category": "Autoimmune",
        "claim_note": "Flares, fatigue, and organ involvement — document unpredictable incapacity episodes.",
    },
    {
        "name": "Schizophrenia",
        "acronym": "SCZ",
        "atlas_slug": "schizophrenia",
        "category": "Mental health",
        "claim_note": "Relapse and cognition — PMB cover does not replace IP functional and own-occupation evidence.",
    },
    {
        "name": "Rheumatoid arthritis",
        "acronym": "RHA",
        "atlas_slug": "rheumatoid-arthritis",
        "category": "Pain & MSK",
        "claim_note": "Grip, stamina, and morning stiffness — link DMARD plan to material manual duties.",
    },
    {
        "name": "Parkinson's disease",
        "acronym": "PAR",
        "atlas_slug": "parkinson-disease",
        "category": "Neurological",
        "claim_note": "Tremor, gait, and medication timing — safety-critical and fine motor duties.",
    },
    {
        "name": "Hyperlipidaemia",
        "acronym": "HYL",
        "atlas_slug": "hyperlipidaemia",
        "category": "Metabolic",
        "claim_note": "PMB focuses on cardiovascular risk reduction — usually secondary to work impact claims.",
    },
    {
        "name": "Multiple sclerosis",
        "acronym": "MSS",
        "atlas_slug": "multiple-sclerosis",
        "category": "Neurological",
        "claim_note": "Relapsing course and fatigue — document EDSS or functional equivalents for insurers.",
    },
    {
        "name": "HIV/AIDS",
        "acronym": "HIV",
        "atlas_slug": "hiv-disease",
        "category": "Infectious",
        "claim_note": "PMB HIV management is separate from income-protection definitions — document ART adherence and complications.",
    },
]

PMB_SECTIONS: list[dict[str, str]] = [
    {
        "id": "overview",
        "title": "What are PMBs?",
        "body": (
            "Prescribed Minimum Benefits (PMBs) are defined benefits ensuring all medical scheme members "
            "can access minimum health services regardless of benefit option. Schemes must cover diagnosis, "
            "treatment, and care for emergencies, ~271 DTP conditions, and 26 CDL chronic diseases."
        ),
    },
    {
        "id": "objectives",
        "title": "PMB objectives",
        "body": (
            "Continuous healthcare even when annual benefits are exhausted; correct payer for PMB treatment "
            "(including state hospital care); minimum care regardless of age or option; and sustainable scheme finances "
            "through better chronic disease management."
        ),
    },
    {
        "id": "dtp",
        "title": "Diagnosis Treatment Pairs (DTPs)",
        "body": (
            "Annexure A to the Medical Schemes Act lists diagnosis–treatment pairs linking a diagnosis to "
            "appropriate treatment. Care should follow evidence-based public-sector protocols where schemes disagree. "
            "Some DTPs include chronic medicine (e.g. HIV, menopause management)."
        ),
    },
    {
        "id": "cdl",
        "title": "Chronic Disease List (CDL)",
        "body": (
            "26 chronic conditions with mandated medication, consultations, and tests. Treatment algorithms "
            "published in the Government Gazette are minimum standards — scheme cover may not be inferior. "
            "Schemes may use protocols, formularies, and Designated Service Providers (DSPs)."
        ),
    },
    {
        "id": "emergency",
        "title": "Emergency conditions",
        "body": (
            "Sudden, unexpected onset requiring immediate treatment or operation — risk of death, organ damage, "
            "or lasting disability without care. Schemes must approve suspected PMB emergencies even before "
            "final diagnosis; confirmation may be requested later. Nearest facility is covered in emergencies."
        ),
    },
    {
        "id": "dsp",
        "title": "Designated Service Providers",
        "body": (
            "Scheme-first-choice providers for PMB conditions. Non-DSP use may trigger co-payments unless no "
            "reasonable DSP exists near home or work. DSPs must deliver without unreasonable delay; if unable, "
            "the scheme remains liable at a non-DSP."
        ),
    },
]

_dtp_by_code: dict[str, dict] | None = None
_dtp_by_slug: dict[str, dict] | None = None
_cdl_by_slug: dict[str, dict] | None = None
_schemes_by_slug: dict[str, dict] | None = None


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    cleaned = html.unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _http_get(url: str, timeout: int = 25) -> str:
    req = Request(url, headers={"User-Agent": CMS_USER_AGENT, "Accept": "*/*"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _enrich_cdl(row: dict) -> dict:
    return {**row, "slug": slugify(row["name"])}


def _build_cdl_index() -> None:
    global _cdl_by_slug
    if _cdl_by_slug is not None:
        return
    _cdl_by_slug = {}
    for row in CDL_CONDITIONS:
        item = _enrich_cdl(row)
        _cdl_by_slug[item["slug"]] = item


def _build_dtp_index() -> None:
    global _dtp_by_code, _dtp_by_slug
    if _dtp_by_code is not None:
        return
    raw = _load_json(DTP_PATH) or []
    _dtp_by_code = {}
    _dtp_by_slug = {}
    for row in raw:
        code = str(row.get("code") or "").strip().upper()
        if not code:
            continue
        item = {
            "code": code,
            "slug": slugify(f"{code}-{row.get('description', '')}"),
            "description": str(row.get("description") or ""),
            "treatment": str(row.get("treatment") or ""),
            "category": str(row.get("category") or "").strip(),
        }
        _dtp_by_code[code] = item
        _dtp_by_slug[item["slug"]] = item


def _build_scheme_index() -> None:
    global _schemes_by_slug
    if _schemes_by_slug is not None:
        return
    payload = _load_json(SCHEMES_PATH) or {}
    _schemes_by_slug = {}
    for row in payload.get("schemes") or []:
        slug = row.get("slug") or slugify(row.get("name", ""))
        _schemes_by_slug[slug] = {**row, "slug": slug}


def cms_stats() -> dict[str, int]:
    _build_scheme_index()
    _build_dtp_index()
    _build_cdl_index()
    open_count = sum(1 for s in (_schemes_by_slug or {}).values() if s.get("type") == "Open")
    return {
        "schemes": len(_schemes_by_slug or {}),
        "schemes_open": open_count,
        "schemes_restricted": len(_schemes_by_slug or {}) - open_count,
        "dtp_conditions": len(_dtp_by_code or {}),
        "cdl_conditions": len(_cdl_by_slug or {}),
        "pmb_sections": len(PMB_SECTIONS),
    }


def cms_data_sources() -> list[dict[str, str]]:
    return [
        {
            "label": "Council for Medical Schemes — PMB",
            "url": CMS_PMB_URL,
            "note": "Primary PMB definitions and consumer guidance.",
        },
        {
            "label": "CMS Industry Report 2023",
            "url": "https://www.medicalschemes.co.za/media-centre/the-medical-schemes-industry-in-2023/",
            "note": "Registered scheme list (71 schemes).",
        },
        {
            "label": "PMB conditions spreadsheet (CMS)",
            "url": "https://www.medicalschemes.co.za/download/2032/prescribed-minimum-benefits/18097/pmblstofallconditions.xlsx",
            "note": "Source for DTP coded list.",
        },
        {
            "label": "CDL treatment algorithms",
            "url": "https://www.medicalschemes.co.za/publications/#2009-2152-wpfd-chronic-disease-list-algorithms",
            "note": "Government Gazette minimum treatment standards.",
        },
    ]


def list_schemes(*, scheme_type: str | None = None) -> list[dict]:
    _build_scheme_index()
    rows = list((_schemes_by_slug or {}).values())
    if scheme_type:
        want = scheme_type.strip().title()
        rows = [r for r in rows if r.get("type") == want]
    return sorted(rows, key=lambda r: (r.get("type", ""), r.get("name", "")))


def get_scheme(slug: str) -> dict | None:
    _build_scheme_index()
    return (_schemes_by_slug or {}).get(slug)


def list_cdl_conditions() -> list[dict]:
    _build_cdl_index()
    return sorted((_cdl_by_slug or {}).values(), key=lambda r: r["name"])


def get_cdl_condition(slug: str) -> dict | None:
    _build_cdl_index()
    return (_cdl_by_slug or {}).get(slug)


def list_dtp_categories() -> list[dict[str, Any]]:
    _build_dtp_index()
    counts: dict[str, int] = {}
    for item in (_dtp_by_code or {}).values():
        cat = item.get("category") or "Other"
        counts[cat] = counts.get(cat, 0) + 1
    return [
        {"name": name, "slug": slugify(name), "count": count}
        for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    ]


def list_dtp_items(*, category_slug: str | None = None, query: str | None = None, limit: int = 500) -> list[dict]:
    _build_dtp_index()
    rows = list((_dtp_by_code or {}).values())
    if category_slug:
        rows = [r for r in rows if slugify(r.get("category", "")) == category_slug]
    q = (query or "").strip().lower()
    if q:
        rows = [
            r for r in rows
            if q in r.get("code", "").lower()
            or q in r.get("description", "").lower()
            or q in r.get("treatment", "").lower()
            or q in r.get("category", "").lower()
        ]
    rows.sort(key=lambda r: (r.get("category", ""), r.get("code", "")))
    return rows[:limit]


def get_dtp(code_or_slug: str) -> dict | None:
    _build_dtp_index()
    key = (code_or_slug or "").strip().upper()
    if key in (_dtp_by_code or {}):
        return _dtp_by_code[key]
    return (_dtp_by_slug or {}).get(code_or_slug)


def search_cms(query: str, *, limit: int = 24) -> dict[str, list[dict]]:
    q = (query or "").strip().lower()
    if not q:
        return {"schemes": [], "cdl": [], "dtp": []}
    schemes = [s for s in list_schemes() if q in s.get("name", "").lower()][:8]
    cdl = [c for c in list_cdl_conditions() if q in c.get("name", "").lower() or q in c.get("acronym", "").lower()][:8]
    dtp = list_dtp_items(query=q, limit=limit - len(schemes) - len(cdl))
    return {"schemes": schemes, "cdl": cdl, "dtp": dtp}


def pmb_explainer() -> dict[str, Any]:
    cache = _load_json(PMB_CACHE_PATH) or {}
    return {
        "sections": PMB_SECTIONS,
        "pmb_pillars": [
            {"title": "Emergency", "detail": "Any emergency medical condition — nearest facility covered."},
            {"title": "DTP conditions", "detail": "271 diagnosis–treatment pairs in Medical Schemes Act Annexure A."},
            {"title": "CDL chronic disease", "detail": "26 listed chronic diseases with algorithm minimum standards."},
        ],
        "diagnosis_based_note": (
            "PMB eligibility uses a diagnosis-based approach — symptoms determine the PMB, "
            "not how the condition was contracted."
        ),
        "cached_excerpt": cache.get("intro") or PMB_SECTIONS[0]["body"],
        "fetched_at": cache.get("fetched_at"),
        "source_url": CMS_PMB_URL,
    }


def related_dtp_for_cdl(condition: dict, *, limit: int = 6) -> list[dict]:
    """Loose text match between CDL name and DTP descriptions."""
    _build_dtp_index()
    name = (condition.get("name") or "").lower()
    tokens = [t for t in re.split(r"[^a-z0-9]+", name) if len(t) > 3]
    if not tokens:
        return []
    matches: list[tuple[int, dict]] = []
    for item in (_dtp_by_code or {}).values():
        blob = f"{item.get('description', '')} {item.get('treatment', '')}".lower()
        score = sum(2 if tok in name else 0 for tok in tokens) + sum(1 for tok in tokens if tok in blob)
        if score >= 2:
            matches.append((score, item))
    matches.sort(key=lambda pair: (-pair[0], pair[1].get("code", "")))
    return [item for _, item in matches[:limit]]


def refresh_pmb_cache(force: bool = False) -> dict[str, Any]:
    if PMB_CACHE_PATH.is_file() and not force:
        age = time.time() - PMB_CACHE_PATH.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            return _load_json(PMB_CACHE_PATH) or {}

    result: dict[str, Any] = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_url": CMS_PMB_URL,
        "intro": PMB_SECTIONS[0]["body"],
        "error": None,
    }
    try:
        raw = _http_get(CMS_PMB_URL)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PMB_HTML_PATH.write_text(raw, encoding="utf-8")
        intro_match = re.search(
            r"Prescribed Minimum Benefits \(PMBs\) are[^<]+",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if intro_match:
            result["intro"] = _strip_html(intro_match.group(0))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        result["error"] = str(exc)
        if PMB_HTML_PATH.is_file():
            raw = PMB_HTML_PATH.read_text(encoding="utf-8", errors="replace")
            intro_match = re.search(
                r"Prescribed Minimum Benefits \(PMBs\) are[^<]+",
                raw,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if intro_match:
                result["intro"] = _strip_html(intro_match.group(0))
    PMB_CACHE_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result