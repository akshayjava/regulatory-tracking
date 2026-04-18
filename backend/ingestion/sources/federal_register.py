"""
Federal Register API ingestion source.
API docs: https://www.federalregister.gov/developers/api/v1
No API key required.
"""
import logging
import re
import time
from datetime import date

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"

AGENCY_VERTICAL_MAP = {
    "financial crimes enforcement network": "fintech",
    "fincen": "crypto",
    "securities and exchange commission": "fintech",
    "sec": "fintech",
    "food and drug administration": "healthcare",
    "fda": "healthcare",
    "centers for medicare": "healthcare",
    "cms": "healthcare",
    "department of health": "healthcare",
    "hhs": "healthcare",
    "consumer financial protection": "fintech",
    "cfpb": "fintech",
    "federal trade commission": "saas",
    "ftc": "saas",
    "office of the comptroller": "fintech",
    "occ": "fintech",
    "national association of insurance": "insurance",
    "internal revenue": "fintech",
    "irs": "fintech",
}

VERTICAL_KEYWORDS = {
    "crypto": ["cryptocurrency", "virtual currency", "digital asset", "blockchain", "bitcoin", "stablecoin"],
    "fintech": ["fintech", "financial technology", "payment", "lending", "banking", "money transmission", "consumer financial"],
    "healthcare": ["health", "medical", "medicare", "medicaid", "hipaa", "telehealth", "drug", "device", "pharmaceutical"],
    "insurance": ["insurance", "insurer", "annuity", "reinsurance", "actuarial", "underwriting"],
    "saas": ["data privacy", "cybersecurity", "software", "artificial intelligence", "cloud", "gdpr", "ccpa", "data security"],
}

DOC_TYPE_MAP = {
    "Rule": "rule",
    "Proposed Rule": "rule",
    "Notice": "notice",
    "Presidential Document": "order",
    "Correction": "notice",
}

STATUS_MAP = {
    "Rule": "final",
    "Proposed Rule": "proposed",
    "Notice": "effective",
    "Presidential Document": "effective",
}


def _detect_verticals(agencies: list[str], title: str, abstract: str) -> list[tuple[str, int, bool]]:
    text = (title + " " + abstract).lower()
    agency_text = " ".join(agencies).lower()

    vertical_scores: dict[str, int] = {}

    for agency in agencies:
        a_lower = agency.lower()
        for key, vertical in AGENCY_VERTICAL_MAP.items():
            if key in a_lower:
                vertical_scores[vertical] = vertical_scores.get(vertical, 0) + 4

    for vertical, keywords in VERTICAL_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            vertical_scores[vertical] = vertical_scores.get(vertical, 0) + hits

    results = []
    for vertical, score in vertical_scores.items():
        if score >= 2:
            results.append((vertical, min(10, score + 2), score >= 6))
    return results


def _doc_to_regulation(doc: dict) -> dict | None:
    try:
        title = doc.get("title", "").strip()
        if not title:
            return None

        doc_number = doc.get("document_number", "").replace("/", "_").replace(" ", "_")
        reg_id = f"fedreg_{doc_number}".lower()

        agencies = [a.get("name", "") for a in doc.get("agencies", [])]
        abstract = doc.get("abstract") or ""
        doc_type = doc.get("type", "Rule")

        verticals = _detect_verticals(agencies, title, abstract)
        if not verticals:
            return None

        pub_date = doc.get("publication_date", str(date.today()))
        effective_date = doc.get("effective_on")

        return {
            "regulation_id": reg_id,
            "title": title[:500],
            "type": DOC_TYPE_MAP.get(doc_type, "notice"),
            "status": STATUS_MAP.get(doc_type, "proposed"),
            "source": "federal_register",
            "summary": abstract[:1000] or title,
            "published_date": pub_date,
            "effective_date": effective_date,
            "deadline_date": None,
            "complexity_score": 6,
            "impact_score": 6,
            "affected_entities": [],
            "keywords": [],
            "citation": doc.get("citation", doc_number),
            "verticals": verticals,
        }
    except Exception as e:
        logger.warning(f"Failed to parse FR document: {e}")
        return None


class FederalRegisterSource:
    """Fetches regulatory documents from the Federal Register API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "LATTICE-RegulatoryPlatform/1.0"

    def fetch(self, limit: int = 100) -> list[dict]:
        """Fetch recent FR documents and return normalized regulation dicts."""
        regulations = []
        page = 1

        while len(regulations) < limit:
            params = {
                "fields[]": ["title", "abstract", "agencies", "publication_date",
                              "effective_on", "document_number", "type", "citation"],
                "per_page": 20,
                "page": page,
                "order": "newest",
                "conditions[type][]": ["RULE", "PRORULE", "NOTICE"],
            }

            try:
                resp = self.session.get(BASE_URL, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                logger.error(f"Federal Register fetch error: {e}")
                break

            docs = data.get("results", [])
            if not docs:
                break

            for doc in docs:
                reg = _doc_to_regulation(doc)
                if reg:
                    regulations.append(reg)

            page += 1
            if len(docs) < 20:
                break
            time.sleep(0.3)

        logger.info(f"FederalRegisterSource: fetched {len(regulations)} relevant regulations")
        return regulations[:limit]
