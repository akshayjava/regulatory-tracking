"""
Healthcare regulatory source — stub with realistic hardcoded data.
Real integration points: FDA API (api.fda.gov), CMS (data.cms.gov), HHS regulations.gov
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

today = date.today()


HEALTHCARE_REGULATIONS = [
    {
        "regulation_id": "hipaa_privacy_rule_45cfr164",
        "title": "HIPAA Privacy Rule (45 CFR Part 164)",
        "type": "rule",
        "status": "effective",
        "source": "hhs",
        "summary": "Establishes national standards for the protection of individually identifiable health information. Covered entities must provide Notice of Privacy Practices and honor patient access requests.",
        "published_date": "2003-04-14",
        "effective_date": "2003-04-14",
        "deadline_date": None,
        "complexity_score": 9,
        "impact_score": 10,
        "affected_entities": ["healthcare_provider", "health_insurer"],
        "keywords": ["HIPAA", "PHI", "privacy", "covered entity", "notice of privacy practices"],
        "citation": "45 CFR Part 164, Subpart E",
        "verticals": [("healthcare", 10, True)],
    },
    {
        "regulation_id": "hipaa_security_rule_45cfr164_304",
        "title": "HIPAA Security Rule (45 CFR §164.304)",
        "type": "rule",
        "status": "effective",
        "source": "hhs",
        "summary": "Administrative, physical, and technical safeguards required for electronic protected health information (ePHI). Annual risk analysis mandatory.",
        "published_date": "2005-04-20",
        "effective_date": "2005-04-20",
        "deadline_date": None,
        "complexity_score": 9,
        "impact_score": 10,
        "affected_entities": ["healthcare_provider", "health_insurer", "medical_device"],
        "keywords": ["HIPAA", "ePHI", "security", "risk analysis", "safeguards"],
        "citation": "45 CFR Part 164, Subpart C",
        "verticals": [("healthcare", 10, True), ("saas", 5, False)],
    },
    {
        "regulation_id": "fda_21cfr820_quality_system",
        "title": "FDA Quality System Regulation (21 CFR Part 820)",
        "type": "rule",
        "status": "effective",
        "source": "fda",
        "summary": "Good Manufacturing Practice requirements for medical device manufacturers. Design controls, production and process controls, corrective and preventive actions required.",
        "published_date": "1996-10-07",
        "effective_date": "1997-06-01",
        "deadline_date": None,
        "complexity_score": 9,
        "impact_score": 9,
        "affected_entities": ["medical_device"],
        "keywords": ["FDA", "QSR", "GMP", "medical device", "design controls", "CAPA"],
        "citation": "21 CFR Part 820",
        "verticals": [("healthcare", 10, True)],
    },
    {
        "regulation_id": "cms_meaningful_use_ehr_2024",
        "title": "CMS Promoting Interoperability (Meaningful Use EHR) 2024",
        "type": "rule",
        "status": "effective",
        "source": "cms",
        "summary": "Hospitals and eligible professionals must use certified EHR technology and report quality measures. Penalties apply for non-participation starting 2024.",
        "published_date": "2024-01-01",
        "effective_date": "2024-01-01",
        "deadline_date": str(today + timedelta(days=90)),
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["healthcare_provider"],
        "keywords": ["EHR", "meaningful use", "interoperability", "CMS", "MIPS"],
        "citation": "42 CFR Part 495",
        "verticals": [("healthcare", 9, True)],
    },
    {
        "regulation_id": "fda_510k_premarket_notification",
        "title": "FDA 510(k) Premarket Notification Requirements",
        "type": "guidance",
        "status": "effective",
        "source": "fda",
        "summary": "Medical device manufacturers must submit 510(k) premarket notifications demonstrating substantial equivalence to legally marketed predicate devices before marketing.",
        "published_date": "2019-11-01",
        "effective_date": "2019-11-01",
        "deadline_date": None,
        "complexity_score": 8,
        "impact_score": 9,
        "affected_entities": ["medical_device"],
        "keywords": ["FDA", "510k", "premarket", "substantial equivalence", "predicate device"],
        "citation": "21 U.S.C. §360(k); 21 CFR Part 807",
        "verticals": [("healthcare", 10, True)],
    },
    {
        "regulation_id": "hitech_breach_notification_2009",
        "title": "HITECH Act Breach Notification Rule",
        "type": "rule",
        "status": "effective",
        "source": "hhs",
        "summary": "Covered entities and business associates must notify affected individuals, HHS, and (in some cases) media of unsecured PHI breaches within 60 days of discovery.",
        "published_date": "2009-09-23",
        "effective_date": "2010-02-22",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 9,
        "affected_entities": ["healthcare_provider", "health_insurer"],
        "keywords": ["HITECH", "breach notification", "PHI", "60 days", "business associate"],
        "citation": "45 CFR §§164.400-414",
        "verticals": [("healthcare", 10, True)],
    },
    {
        "regulation_id": "cms_interoperability_rule_2020",
        "title": "CMS Interoperability and Patient Access Final Rule",
        "type": "rule",
        "status": "effective",
        "source": "cms",
        "summary": "Payers must implement FHIR-based Patient Access APIs by 2021. Provider Directory APIs required. Information blocking provisions enforced by ONC.",
        "published_date": "2020-05-01",
        "effective_date": "2021-07-01",
        "deadline_date": str(today + timedelta(days=60)),
        "complexity_score": 8,
        "impact_score": 8,
        "affected_entities": ["health_insurer", "healthcare_provider"],
        "keywords": ["FHIR", "interoperability", "patient access", "information blocking", "CMS"],
        "citation": "CMS-9115-F",
        "verticals": [("healthcare", 9, True), ("saas", 4, False)],
    },
    {
        "regulation_id": "state_rx_pdmp_requirements",
        "title": "State Prescription Drug Monitoring Programs (PDMP) Requirements",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "49 states mandate PDMP registration and query requirements for prescribers. Must query PDMP before prescribing controlled substances in most states.",
        "published_date": "2023-01-01",
        "effective_date": "2023-01-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["healthcare_provider"],
        "keywords": ["PDMP", "controlled substances", "prescription monitoring", "DEA"],
        "citation": "State-specific (see NAMSDL state law chart)",
        "verticals": [("healthcare", 8, False)],
    },
    {
        "regulation_id": "cms_no_surprises_act_2022",
        "title": "No Surprises Act — Surprise Billing Protections",
        "type": "rule",
        "status": "effective",
        "source": "cms",
        "summary": "Protects patients from surprise medical bills. Out-of-network providers cannot bill patients beyond in-network cost sharing. Independent dispute resolution process established.",
        "published_date": "2022-01-01",
        "effective_date": "2022-01-01",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["healthcare_provider", "health_insurer"],
        "keywords": ["surprise billing", "No Surprises Act", "IDR", "out-of-network", "cost sharing"],
        "citation": "26 CFR Part 54; 29 CFR Part 2590; 45 CFR Part 149",
        "verticals": [("healthcare", 9, True), ("insurance", 7, False)],
    },
    {
        "regulation_id": "fda_digital_health_center_2023",
        "title": "FDA Digital Health Center of Excellence — Software as Medical Device (SaMD)",
        "type": "guidance",
        "status": "effective",
        "source": "fda",
        "summary": "Guidance for software functions that meet the definition of a medical device. Clarifies which clinical decision support software requires 510(k) clearance.",
        "published_date": "2023-06-01",
        "effective_date": "2023-06-01",
        "deadline_date": None,
        "complexity_score": 8,
        "impact_score": 8,
        "affected_entities": ["medical_device", "saas_company", "healthcare_provider"],
        "keywords": ["SaMD", "digital health", "clinical decision support", "510k", "FDA"],
        "citation": "21st Century Cures Act §3060",
        "verticals": [("healthcare", 9, True), ("saas", 6, False)],
    },
]


class HealthcareSource:
    """
    Healthcare regulatory source.
    Currently returns hardcoded seed data.

    Future integrations:
    - FDA API: https://api.fda.gov/drug/label.json (drug labeling)
    - CMS Open Data: https://data.cms.gov/api/1 (Medicare/Medicaid rules)
    - HHS regulations.gov: https://api.regulations.gov/v4/documents
    - ONC Health IT: https://www.healthit.gov/api
    """

    def fetch(self) -> list[dict]:
        logger.info(f"HealthcareSource: returning {len(HEALTHCARE_REGULATIONS)} hardcoded regulations")
        return HEALTHCARE_REGULATIONS
