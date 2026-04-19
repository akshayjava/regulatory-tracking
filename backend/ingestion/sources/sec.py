"""
SEC EDGAR RSS API ingestion source.
"""
from __future__ import annotations
import logging
import xml.etree.ElementTree as ET
from datetime import date

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

VERTICAL_KEYWORDS = {
    "crypto": ["cryptocurrency", "virtual currency", "digital asset", "blockchain", "bitcoin", "stablecoin"],
    "fintech": ["fintech", "financial technology", "payment", "lending", "banking", "money transmission", "consumer financial", "securities", "broker", "dealer", "investment", "advisor", "form"],
}


def _detect_verticals(title: str) -> list[tuple[str, int, bool]]:
    text = title.lower()

    vertical_scores: dict[str, int] = {}

    # Base SEC items are typically fintech related
    vertical_scores["fintech"] = 4

    for vertical, keywords in VERTICAL_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            vertical_scores[vertical] = vertical_scores.get(vertical, 0) + hits

    results = []
    for vertical, score in vertical_scores.items():
        if score >= 2:
            results.append((vertical, min(10, score + 2), score >= 6))
    return results


def _entry_to_regulation(entry: ET.Element) -> dict | None:
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    try:
        title_el = entry.find('atom:title', ns)
        if title_el is None or not title_el.text:
            return None

        title = title_el.text.strip()

        id_el = entry.find('atom:id', ns)
        reg_id = "sec_unknown"
        if id_el is not None and id_el.text:
            # urn:tag:sec.gov,2008:accession-number=0001193125-26-162189
            if "accession-number=" in id_el.text:
                doc_number = id_el.text.split("accession-number=")[1]
                reg_id = f"sec_{doc_number}".lower()

        updated_el = entry.find('atom:updated', ns)
        pub_date = str(date.today())
        if updated_el is not None and updated_el.text:
            pub_date = updated_el.text[:10]

        summary_el = entry.find('atom:summary', ns)
        summary = title
        if summary_el is not None and summary_el.text:
            summary = summary_el.text.strip()

        category_el = entry.find('atom:category', ns)
        form_type = "form"
        if category_el is not None:
            form_type = category_el.get('term', 'form')

        verticals = _detect_verticals(title + " " + summary)
        if not verticals:
            verticals = [("fintech", 5, False)]

        return {
            "regulation_id": reg_id.replace("-", "_"),
            "title": title[:500],
            "type": "notice",
            "status": "effective",
            "source": "sec",
            "summary": summary[:1000] or title,
            "published_date": pub_date,
            "effective_date": pub_date,
            "deadline_date": None,
            "complexity_score": 7,
            "impact_score": 7,
            "affected_entities": [],
            "keywords": [form_type] if form_type else [],
            "citation": form_type,
            "verticals": verticals,
            "agency": "SEC"
        }
    except Exception as e:
        logger.warning(f"Failed to parse SEC entry: {e}")
        return None


class SecSource:
    """Fetches regulatory documents from the SEC EDGAR RSS."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "LATTICE-RegulatoryPlatform/1.0 (akshayjava@gmail.com)"

    def fetch(self, limit: int = 100) -> list[dict]:
        """Fetch recent SEC documents and return normalized regulation dicts."""
        regulations = []

        params = {
            "action": "getcurrent",
            "type": "",
            "company": "",
            "dateb": "",
            "owner": "include",
            "count": str(limit),
            "output": "atom"
        }

        try:
            resp = self.session.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()

            # Parse XML
            root = ET.fromstring(resp.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)

            for entry in entries:
                reg = _entry_to_regulation(entry)
                if reg:
                    regulations.append(reg)

        except requests.RequestException as e:
            logger.error(f"SEC EDGAR fetch error: {e}")
        except ET.ParseError as e:
            logger.error(f"SEC EDGAR XML parse error: {e}")

        logger.info(f"SecSource: fetched {len(regulations)} relevant regulations")
        return regulations[:limit]
