"""
Congress.gov API ingestion source.
API docs: https://api.congress.gov/
Free API key: https://api.congress.gov/sign-up/
"""
import logging
import os
import re
import time
from datetime import date, datetime

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.congress.gov/v3"

VERTICAL_KEYWORDS = {
    "crypto": ["cryptocurrency", "crypto", "digital asset", "virtual currency", "blockchain", "bitcoin", "stablecoin", "defi", "nft", "token"],
    "fintech": ["fintech", "financial technology", "payment", "lending", "banking", "money transmission", "consumer finance", "credit"],
    "healthcare": ["health", "medical", "medicare", "medicaid", "hipaa", "fda", "telehealth", "pharmaceutical", "drug", "device"],
    "insurance": ["insurance", "insurer", "underwriting", "annuity", "reinsurance", "actuarial"],
    "saas": ["data privacy", "cybersecurity", "software", "technology", "artificial intelligence", "ai", "cloud", "gdpr", "ccpa"],
}


def _detect_verticals(text: str) -> list[tuple[str, int, bool]]:
    """Return list of (vertical, relevance_score, is_critical) based on keyword matching."""
    text_lower = text.lower()
    results = []
    for vertical, keywords in VERTICAL_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits >= 2:
            score = min(10, hits + 4)
            results.append((vertical, score, hits >= 4))
        elif hits == 1:
            results.append((vertical, 4, False))
    return results


def _bill_to_regulation(bill: dict) -> dict | None:
    """Normalize a Congress.gov bill response to LATTICE regulation schema."""
    try:
        title = bill.get("title", "").strip()
        if not title:
            return None

        bill_type = bill.get("type", "HR").lower()
        congress = bill.get("congress", "")
        number = bill.get("number", "")
        reg_id = f"congress_{bill_type}{number}_{congress}".lower().replace(" ", "_")

        action_date = bill.get("latestAction", {}).get("actionDate", "")
        update_date = bill.get("updateDate", "")

        status_map = {"introduced": "proposed", "passed house": "proposed", "passed senate": "proposed",
                      "enacted": "effective", "signed": "effective", "vetoed": "withdrawn"}
        latest_action = (bill.get("latestAction", {}).get("text") or "").lower()
        status = "proposed"
        for key, val in status_map.items():
            if key in latest_action:
                status = val
                break

        summary = bill.get("title", "")
        verticals = _detect_verticals(title + " " + summary)
        if not verticals:
            return None  # Skip non-regulatory bills

        keywords = [kw for vertical, _, _ in verticals for kw in VERTICAL_KEYWORDS.get(vertical, [])][:10]

        return {
            "regulation_id": reg_id,
            "title": title[:500],
            "type": "bill",
            "status": status,
            "source": "congress",
            "summary": summary[:1000],
            "published_date": action_date or update_date or str(date.today()),
            "effective_date": None,
            "deadline_date": None,
            "complexity_score": 5,
            "impact_score": 6,
            "affected_entities": [],
            "keywords": list(set(keywords))[:10],
            "citation": f"{bill_type.upper()} {number}, {congress}th Congress",
            "verticals": verticals,
        }
    except Exception as e:
        logger.warning(f"Failed to parse bill: {e}")
        return None


class CongressSource:
    """Fetches bills from Congress.gov API."""

    def __init__(self):
        self.api_key = os.environ.get("CONGRESS_API_KEY", "")
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "LATTICE-RegulatoryPlatform/1.0"

    def fetch(self, limit: int = 100) -> list[dict]:
        """Fetch recent bills and return normalized regulation dicts."""
        regulations = []
        offset = 0
        fetched = 0

        while fetched < limit:
            batch = min(20, limit - fetched)
            params = {
                "format": "json",
                "limit": batch,
                "offset": offset,
                "sort": "updateDate+desc",
            }
            if self.api_key:
                params["api_key"] = self.api_key

            try:
                resp = self.session.get(f"{BASE_URL}/bill", params=params, timeout=15)
                if resp.status_code == 429:
                    logger.warning("Congress.gov rate limit hit, sleeping 5s")
                    time.sleep(5)
                    continue
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                logger.error(f"Congress.gov fetch error: {e}")
                break

            bills = data.get("bills", [])
            if not bills:
                break

            for bill in bills:
                reg = _bill_to_regulation(bill)
                if reg:
                    regulations.append(reg)

            fetched += len(bills)
            offset += len(bills)

            if len(bills) < batch:
                break

            time.sleep(0.5)  # Respect rate limits

        logger.info(f"CongressSource: fetched {len(regulations)} relevant regulations from {fetched} bills")
        return regulations
