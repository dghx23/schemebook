"""Shared clinical procedure concepts curated from an Australian browsing directory.

This is a small cross-jurisdictional vocabulary, not Australian fee/service data
and not a South African coding, coverage, indication or clinical guideline.
The factual concepts are independently grouped; source prose and service codes
are not copied into Core common. Local teams must validate clinical usage.
"""
from __future__ import annotations
from typing import Any
from unicodedata import normalize
import re

SOURCE_URLS = (
    "https://medicalcostsfinder.health.gov.au/procedures/",
    "https://medicalcostsfinder.health.gov.au/procedures/?mode=category",
)
CONCEPT_GROUPS = {
    "Reproductive health and pregnancy": [
        "Oocyte retrieval",
        "Embryo transfer",
        "Caesarean delivery",
        "Vaginal delivery",
        "Hysteroscopy",
        "Hysterectomy",
        "Laparoscopy",
        "Management of pregnancy loss"
    ],
    "Musculoskeletal": [
        "Carpal tunnel release",
        "Ankle arthroscopy",
        "Knee arthroscopy",
        "Hip arthroscopy",
        "Knee reconstruction",
        "Shoulder repair",
        "Hip replacement",
        "Knee replacement",
        "Ankle replacement"
    ],
    "Breast and reconstructive": [
        "Breast biopsy",
        "Lumpectomy",
        "Mastectomy",
        "Breast reconstruction",
        "Breast reduction",
        "Skin flap repair"
    ],
    "Eye": [
        "Cataract surgery",
        "Corneal graft",
        "Retinal detachment repair",
        "Intravitreal injection",
        "Retinal laser",
        "Pterygium surgery"
    ],
    "Cancer care": [
        "Chemotherapy",
        "Immunotherapy",
        "Lymph node biopsy",
        "Tumour excision"
    ],
    "Kidney and urinary": [
        "Dialysis",
        "Cystoscopy",
        "Nephrectomy",
        "Kidney stone procedure",
        "Prostate biopsy",
        "Prostatectomy"
    ],
    "Digestive": [
        "Colonoscopy",
        "Gastroscopy",
        "Cholecystectomy",
        "Bowel resection",
        "Haemorrhoid treatment",
        "Hernia repair"
    ],
    "Ear nose and throat": [
        "Sinus surgery",
        "Septoplasty",
        "Tonsillectomy",
        "Adenoidectomy",
        "Grommet insertion",
        "Cochlear implantation"
    ],
    "Cardiovascular": [
        "Coronary angiography",
        "Coronary bypass surgery",
        "Cardiac ablation",
        "Pacemaker insertion",
        "Heart valve repair",
        "Heart valve replacement",
        "Coronary stenting"
    ],
    "Respiratory and thoracic": [
        "Bronchoscopy",
        "Thoracoscopy",
        "Lung resection"
    ],
    "Skin": [
        "Skin lesion removal",
        "Melanoma excision",
        "Basal cell carcinoma excision",
        "Wound debridement"
    ],
    "Pain and sleep": [
        "Facet joint denervation",
        "Sleep study"
    ],
    "Weight management": [
        "Gastric banding",
        "Gastric bypass",
        "Sleeve gastrectomy"
    ]
}

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize("NFKD", value).encode("ascii", "ignore").decode().lower()).strip("-")

def procedure_concepts(query: str = "") -> list[dict[str, Any]]:
    needle = query.strip().casefold()
    return [
        {"id": "procedure." + _slug(name), "name": name,
         "category": group, "category_slug": _slug(group),
         "jurisdiction": "common", "source_url": SOURCE_URLS[1],
         "review_status": "generic terminology; ZA validation pending"}
        for group, names in CONCEPT_GROUPS.items() for name in names
        if not needle or needle in name.casefold() or needle in group.casefold()
    ]

def procedure_categories() -> list[dict[str, Any]]:
    return [
        {"slug": _slug(group), "name": group, "concept_count": len(names),
         "jurisdiction": "common", "review_status": "ZA validation pending"}
        for group, names in CONCEPT_GROUPS.items()
    ]

def source_registry_row() -> dict[str, str]:
    return {
        "domain": "Clinical procedures",
        "domain_url": "atlascore.browse",
        "source": "Medical Costs Finder — generic procedure terminology (derived)",
        "feed_type": "Curated universal concept subset, source linked",
        "api_access": SOURCE_URLS[1],
        "refresh": "On review of source and ZA clinical validation",
        "consumed_by": "Core common · Core ZA · ClinicalAtlas ZA",
        "status": "Seeded generic vocabulary; not validated as SA clinical coding or coverage",
    }
