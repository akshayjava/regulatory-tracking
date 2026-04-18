"""
LegiScan state legislature source — stub with realistic hardcoded data.
Real integration: https://legiscan.com/legiscan-api (requires paid key)
Free tier available for limited requests.
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

today = date.today()


STATE_REGULATIONS = [
    {
        "regulation_id": "ca_ab_2930_ai_regulation_2024",
        "title": "California AB 2930 — Automated Decision Systems Accountability Act",
        "type": "bill",
        "status": "proposed",
        "source": "state",
        "summary": "Requires employers and businesses using automated decision systems to conduct impact assessments and provide notice to affected individuals. Covers AI hiring, lending, and credit decisions.",
        "published_date": "2024-02-15",
        "effective_date": None,
        "deadline_date": str(today + timedelta(days=120)),
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["saas_company", "fintech_lender"],
        "keywords": ["AI", "automated decision", "California", "impact assessment", "algorithmic accountability"],
        "citation": "Cal. AB 2930 (2024)",
        "verticals": [("saas", 9, True), ("fintech", 7, False)],
    },
    {
        "regulation_id": "ny_dfs_23nycrr500_cybersecurity",
        "title": "NY DFS Cybersecurity Regulation (23 NYCRR 500) — 2023 Amendment",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "New York financial services companies must implement comprehensive cybersecurity programs. 2023 amendments add CISO requirements, board reporting, and 72-hour incident reporting.",
        "published_date": "2023-11-01",
        "effective_date": "2024-04-29",
        "deadline_date": str(today + timedelta(days=30)),
        "complexity_score": 8,
        "impact_score": 9,
        "affected_entities": ["bank", "insurer", "fintech_lender", "crypto_exchange"],
        "keywords": ["NY DFS", "cybersecurity", "500", "CISO", "incident reporting", "New York"],
        "citation": "23 NYCRR Part 500",
        "verticals": [("fintech", 10, True), ("crypto", 8, True), ("insurance", 7, False)],
    },
    {
        "regulation_id": "tx_hb_1709_data_privacy_2023",
        "title": "Texas Data Privacy and Security Act (HB 1709)",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Texas comprehensive data privacy law effective July 2024. Grants consumers rights to access, delete, and opt out of sale of personal data. Applies to businesses processing data of 100K+ Texas residents.",
        "published_date": "2023-06-18",
        "effective_date": "2024-07-01",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 7,
        "affected_entities": ["saas_company", "fintech_lender"],
        "keywords": ["Texas", "data privacy", "TDPSA", "consumer rights", "opt-out"],
        "citation": "Tex. Bus. & Com. Code §541",
        "verticals": [("saas", 9, True), ("fintech", 5, False)],
    },
    {
        "regulation_id": "il_biometric_bipa_740ilcs14",
        "title": "Illinois Biometric Information Privacy Act (BIPA)",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Companies collecting biometric data (fingerprints, facial recognition, retina scans) must obtain written consent and have a publicly available retention policy. Private right of action with $1,000-$5,000 per violation.",
        "published_date": "2008-10-03",
        "effective_date": "2008-10-03",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["saas_company", "healthcare_provider"],
        "keywords": ["BIPA", "biometric", "Illinois", "facial recognition", "fingerprint", "consent"],
        "citation": "740 ILCS 14",
        "verticals": [("saas", 9, True), ("healthcare", 5, False)],
    },
    {
        "regulation_id": "wa_my_health_my_data_act_2023",
        "title": "Washington My Health My Data Act (MHMDA)",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Broadest health data privacy law in the US. Covers consumer health data outside HIPAA. Geofencing near healthcare facilities prohibited. Private right of action.",
        "published_date": "2023-04-27",
        "effective_date": "2024-03-31",
        "deadline_date": None,
        "complexity_score": 8,
        "impact_score": 8,
        "affected_entities": ["saas_company", "healthcare_provider", "health_insurer"],
        "keywords": ["Washington", "health data", "MHMDA", "consumer health", "geofencing"],
        "citation": "RCW Chapter 70.372",
        "verticals": [("healthcare", 9, True), ("saas", 8, True)],
    },
    {
        "regulation_id": "co_money_transmitter_crypto_2023",
        "title": "Colorado Money Transmitter Act — Cryptocurrency Amendments",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Colorado amended its Money Transmitter Act to include virtual currency transmitters. Crypto businesses must obtain state license, maintain reserves, and file quarterly reports.",
        "published_date": "2023-01-01",
        "effective_date": "2023-07-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["crypto_exchange", "payment_processor"],
        "keywords": ["Colorado", "money transmitter", "crypto", "license", "virtual currency"],
        "citation": "Colo. Rev. Stat. §11-110-101",
        "verticals": [("crypto", 8, True), ("fintech", 6, False)],
    },
    {
        "regulation_id": "fl_sb_264_cryptocurrency_2023",
        "title": "Florida SB 264 — Digital Assets and Financial Technology",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Florida law regulating digital asset issuers and exchanges. Requires registration with OFR, customer disclosures, and reserve requirements. Exemptions for small issuers.",
        "published_date": "2023-05-12",
        "effective_date": "2023-07-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["crypto_exchange", "fintech_lender"],
        "keywords": ["Florida", "digital assets", "OFR", "registration", "cryptocurrency"],
        "citation": "Fla. Stat. §560.103",
        "verticals": [("crypto", 8, True), ("fintech", 5, False)],
    },
    {
        "regulation_id": "nj_consumer_data_privacy_2024",
        "title": "New Jersey Data Privacy Act (SB 332)",
        "type": "rule",
        "status": "final",
        "source": "state",
        "summary": "New Jersey comprehensive consumer data privacy law effective January 2025. Right to access, correct, delete, and opt out of targeted advertising and sale of personal data.",
        "published_date": "2024-01-16",
        "effective_date": "2025-01-15",
        "deadline_date": str(today + timedelta(days=45)),
        "complexity_score": 7,
        "impact_score": 7,
        "affected_entities": ["saas_company", "fintech_lender"],
        "keywords": ["New Jersey", "NJDPA", "data privacy", "consumer rights", "opt-out"],
        "citation": "N.J. Stat. §56:8-166.1 et seq.",
        "verticals": [("saas", 9, True), ("fintech", 4, False)],
    },
    {
        "regulation_id": "ma_201cmr17_data_protection",
        "title": "Massachusetts 201 CMR 17 — Standards for Protection of Personal Information",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Massachusetts businesses must implement comprehensive written information security programs for personal information of MA residents. Encryption required for transmitted and stored data.",
        "published_date": "2010-03-01",
        "effective_date": "2010-03-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["saas_company", "fintech_lender", "healthcare_provider"],
        "keywords": ["Massachusetts", "201 CMR 17", "WISP", "encryption", "personal information"],
        "citation": "201 CMR 17.00",
        "verticals": [("saas", 8, True), ("fintech", 6, False), ("healthcare", 4, False)],
    },
    {
        "regulation_id": "ct_insurance_data_security_2020",
        "title": "Connecticut Insurance Data Security Law (PA 20-211)",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Connecticut insurance licensees must maintain comprehensive information security programs aligned with NAIC Model Law. Annual certification to Insurance Commissioner required.",
        "published_date": "2020-10-01",
        "effective_date": "2020-10-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["insurer", "health_insurer"],
        "keywords": ["Connecticut", "insurance", "data security", "NAIC", "information security program"],
        "citation": "Conn. Gen. Stat. §38a-999b",
        "verticals": [("insurance", 9, True)],
    },
]


class LegiScanSource:
    """
    State legislation source using LegiScan API.
    Currently returns hardcoded seed data.

    Real integration with LegiScan API:
    - Base URL: https://api.legiscan.com/
    - Key endpoints: getMasterList, getBill, getDataset
    - Requires paid API key from https://legiscan.com/legiscan-api
    - Free tier: 30,000 queries/month

    Example real call:
        import requests
        key = os.environ['LEGISCAN_API_KEY']
        resp = requests.get(f'https://api.legiscan.com/?key={key}&op=getMasterList&state=CA')
    """

    def fetch(self) -> list[dict]:
        logger.info(f"LegiScanSource: returning {len(STATE_REGULATIONS)} hardcoded state regulations")
        return STATE_REGULATIONS
