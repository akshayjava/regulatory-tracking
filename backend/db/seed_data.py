"""
LATTICE - Seed Data Script
Populates the database with agencies, sources, and sample regulations.
Usage: python backend/db/seed_data.py
"""
import json
import os
import sqlite3
from datetime import date, datetime, timedelta

DB_PATH = os.environ.get("DB_PATH", "lattice.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_schema(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()


# ------------------------------------------------------------------ #
# AGENCIES
# ------------------------------------------------------------------ #
AGENCIES = [
    ("Financial Crimes Enforcement Network", "FinCEN", "https://www.fincen.gov", "https://api.fincen.gov"),
    ("Securities and Exchange Commission", "SEC", "https://www.sec.gov", "https://data.sec.gov/submissions"),
    ("Food and Drug Administration", "FDA", "https://www.fda.gov", "https://api.fda.gov"),
    ("Federal Trade Commission", "FTC", "https://www.ftc.gov", None),
    ("Office of the Comptroller of the Currency", "OCC", "https://www.occ.gov", None),
    ("Consumer Financial Protection Bureau", "CFPB", "https://www.consumerfinance.gov", "https://api.consumerfinance.gov/data/hmda"),
    ("Centers for Medicare & Medicaid Services", "CMS", "https://www.cms.gov", "https://data.cms.gov/api/1"),
    ("Office of Foreign Assets Control", "OFAC", "https://ofac.treasury.gov", "https://ofac.treasury.gov/system/files/126/cons_prim.xml"),
    ("Internal Revenue Service", "IRS", "https://www.irs.gov", None),
]

# ------------------------------------------------------------------ #
# REGULATORY SOURCES
# ------------------------------------------------------------------ #
SOURCES = [
    ("Congress.gov", "CONGRESS", "https://www.congress.gov", "https://api.congress.gov/v3/bill"),
    ("Federal Register", "FEDREG", "https://www.federalregister.gov", "https://www.federalregister.gov/api/v1/documents.json"),
    ("LegiScan (State Legislatures)", "LEGISCAN", "https://legiscan.com", "https://api.legiscan.com"),
    ("FDA API", "FDA_API", "https://api.fda.gov", "https://api.fda.gov/drug/event.json"),
    ("SEC EDGAR", "EDGAR", "https://www.sec.gov/cgi-bin/browse-edgar", "https://data.sec.gov/submissions"),
]

# ------------------------------------------------------------------ #
# SEED REGULATIONS  (15 across all 5 verticals)
# ------------------------------------------------------------------ #
today = date.today()

REGULATIONS = [
    # --- CRYPTO (4) ---
    {
        "regulation_id": "fincen_crypto_vasp_guidance_2024",
        "title": "FinCEN Guidance on Virtual Asset Service Providers (VASPs)",
        "type": "guidance",
        "status": "effective",
        "source": "fincen",
        "summary": "Cryptocurrency exchanges and custodians must implement KYC, AML, and OFAC screening. SAR filing required within 30 days of suspicious activity detection.",
        "published_date": "2024-01-15",
        "effective_date": "2024-03-15",
        "deadline_date": str(today + timedelta(days=45)),
        "complexity_score": 8,
        "impact_score": 10,
        "affected_entities": ["crypto_exchange", "crypto_custodian", "defi_protocol"],
        "keywords": ["VASP", "KYC", "AML", "OFAC", "SAR", "cryptocurrency"],
        "citation": "31 CFR 1010.100(ff)",
        "agency": "FinCEN",
        "verticals": [("crypto", 10, True), ("fintech", 7, False)],
        "entities": [
            ("crypto_exchange", {"kyc": "Collect name/address/ID for transactions >$3,000", "aml": "Ongoing transaction monitoring", "ofac": "Screen all customers vs. OFAC SDN list", "sar": "File within 30 days of detection", "recordkeeping": "5 years"}),
            ("crypto_custodian", {"kyc": "Same as exchange", "aml": "Enhanced due diligence for high-risk customers"}),
        ],
    },
    {
        "regulation_id": "sec_crypto_asset_framework_2024",
        "title": "SEC Framework for Crypto Asset Securities",
        "type": "rule",
        "status": "proposed",
        "source": "sec",
        "summary": "Proposed framework classifying certain crypto assets as securities subject to SEC registration and disclosure requirements.",
        "published_date": "2024-02-01",
        "effective_date": None,
        "deadline_date": str(today + timedelta(days=90)),
        "complexity_score": 9,
        "impact_score": 9,
        "affected_entities": ["crypto_exchange", "broker_dealer", "investment_advisor"],
        "keywords": ["crypto", "securities", "registration", "disclosure", "Howey test"],
        "citation": "Securities Act of 1933 §5",
        "agency": "SEC",
        "verticals": [("crypto", 10, True), ("fintech", 6, False)],
        "entities": [
            ("crypto_exchange", {"registration": "Register as national securities exchange or ATS", "disclosure": "File Form S-1 for token offerings"}),
        ],
    },
    {
        "regulation_id": "ofac_crypto_sanctions_2024",
        "title": "OFAC Enhanced Sanctions Screening for Cryptocurrency Transactions",
        "type": "enforcement",
        "status": "effective",
        "source": "ofac",
        "summary": "Enhanced sanctions screening requirements for all cryptocurrency transactions. Wallet address screening against OFAC SDN and Blocked Persons lists required.",
        "published_date": "2024-01-20",
        "effective_date": "2024-01-20",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 10,
        "affected_entities": ["crypto_exchange", "crypto_custodian", "payment_processor"],
        "keywords": ["OFAC", "sanctions", "SDN", "wallet screening", "cryptocurrency"],
        "citation": "50 U.S.C. §1705",
        "agency": "OFAC",
        "verticals": [("crypto", 10, True), ("fintech", 8, True)],
        "entities": [
            ("crypto_exchange", {"screening": "Real-time wallet address screening", "blocking": "Block and report transactions involving sanctioned addresses"}),
        ],
    },
    {
        "regulation_id": "irs_crypto_reporting_2025",
        "title": "IRS Digital Asset Reporting Requirements (Form 1099-DA)",
        "type": "rule",
        "status": "final",
        "source": "irs",
        "summary": "Brokers must report digital asset transactions on new Form 1099-DA starting 2025. Covers exchanges, hosted wallet providers, and certain DeFi platforms.",
        "published_date": "2024-06-28",
        "effective_date": "2025-01-01",
        "deadline_date": str(today + timedelta(days=30)),
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["crypto_exchange", "crypto_custodian"],
        "keywords": ["1099-DA", "digital asset", "tax reporting", "broker", "cost basis"],
        "citation": "26 U.S.C. §6045",
        "agency": "IRS",
        "verticals": [("crypto", 9, True), ("fintech", 4, False)],
        "entities": [
            ("crypto_exchange", {"reporting": "File 1099-DA for each customer transaction", "cost_basis": "Track and report customer cost basis"}),
        ],
    },
    # --- FINTECH (3) ---
    {
        "regulation_id": "occ_fintech_partnership_guidance_2023",
        "title": "OCC Guidance on Bank-Fintech Partnerships",
        "type": "guidance",
        "status": "effective",
        "source": "federal_register",
        "summary": "Guidelines for national banks entering partnerships with fintech companies. Banks retain compliance responsibility and must conduct enhanced due diligence.",
        "published_date": "2023-12-01",
        "effective_date": "2023-12-01",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["bank", "fintech_lender"],
        "keywords": ["fintech", "bank partnership", "due diligence", "third-party risk"],
        "citation": "12 CFR Part 30",
        "agency": "OCC",
        "verticals": [("fintech", 9, True), ("crypto", 3, False)],
        "entities": [
            ("bank", {"due_diligence": "Enhanced third-party risk assessment for fintech partners", "oversight": "Ongoing monitoring of fintech partner compliance"}),
            ("fintech_lender", {"compliance": "Meet bank-equivalent compliance standards"}),
        ],
    },
    {
        "regulation_id": "cfpb_open_banking_rule_1033_2024",
        "title": "CFPB Open Banking Personal Financial Data Rights Rule (Section 1033)",
        "type": "rule",
        "status": "final",
        "source": "federal_register",
        "summary": "Consumers have the right to access and share their financial data with authorized third parties. Financial institutions must provide standardized data access.",
        "published_date": "2024-10-22",
        "effective_date": "2026-04-01",
        "deadline_date": str(today + timedelta(days=60)),
        "complexity_score": 8,
        "impact_score": 9,
        "affected_entities": ["bank", "fintech_lender", "payment_processor"],
        "keywords": ["open banking", "1033", "data portability", "consumer rights", "API"],
        "citation": "12 U.S.C. §5533",
        "agency": "CFPB",
        "verticals": [("fintech", 10, True), ("saas", 5, False)],
        "entities": [
            ("bank", {"api": "Provide consumer-permissioned data access API", "format": "Standardized data format (FDATA standards)", "timeline": "Large banks: 2026, small banks: 2030"}),
            ("fintech_lender", {"data_access": "Can access consumer financial data with permission"}),
        ],
    },
    {
        "regulation_id": "ccpa_2020_california_privacy",
        "title": "California Consumer Privacy Act (CCPA) and CPRA Amendments",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "California consumers have rights to know, delete, opt-out of sale, and correct their personal information. Businesses must provide privacy notices and honor opt-out requests.",
        "published_date": "2020-01-01",
        "effective_date": "2023-01-01",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["fintech_lender", "saas_company", "payment_processor"],
        "keywords": ["CCPA", "CPRA", "privacy", "California", "consumer rights", "data deletion"],
        "citation": "Cal. Civ. Code §1798.100",
        "agency": "FTC",
        "verticals": [("fintech", 7, False), ("saas", 10, True), ("healthcare", 5, False)],
        "entities": [
            ("saas_company", {"privacy_notice": "Post detailed privacy notice on website", "opt_out": "Honor consumer opt-out of data sale within 15 days", "deletion": "Delete consumer data within 45 days of request"}),
        ],
    },
    # --- HEALTHCARE (3) ---
    {
        "regulation_id": "hipaa_security_rule_update_2024",
        "title": "HIPAA Security Rule Modernization (Proposed)",
        "type": "rule",
        "status": "proposed",
        "source": "hhs",
        "summary": "HHS proposes significant updates to HIPAA Security Rule including mandatory MFA, annual technology asset inventories, and 72-hour breach notification for all covered entities.",
        "published_date": "2024-12-27",
        "effective_date": None,
        "deadline_date": str(today + timedelta(days=180)),
        "complexity_score": 9,
        "impact_score": 10,
        "affected_entities": ["healthcare_provider", "health_insurer", "medical_device"],
        "keywords": ["HIPAA", "security rule", "MFA", "breach notification", "PHI", "ePHI"],
        "citation": "45 CFR Parts 160 and 164",
        "agency": "CMS",
        "verticals": [("healthcare", 10, True), ("saas", 4, False)],
        "entities": [
            ("healthcare_provider", {"mfa": "Mandatory MFA for all ePHI systems", "inventory": "Annual technology asset inventory", "breach": "72-hour notification to HHS and patients", "risk_analysis": "Annual security risk analysis required"}),
            ("health_insurer", {"same": "Same requirements as providers for claims data systems"}),
        ],
    },
    {
        "regulation_id": "fda_software_device_guidance_2023",
        "title": "FDA Guidance: Cybersecurity in Medical Devices",
        "type": "guidance",
        "status": "effective",
        "source": "fda",
        "summary": "Medical device manufacturers must implement cybersecurity controls throughout the product lifecycle. Premarket submissions must include a Software Bill of Materials (SBOM).",
        "published_date": "2023-09-27",
        "effective_date": "2023-10-01",
        "deadline_date": None,
        "complexity_score": 8,
        "impact_score": 8,
        "affected_entities": ["medical_device", "healthcare_provider"],
        "keywords": ["FDA", "medical device", "cybersecurity", "SBOM", "premarket"],
        "citation": "21 U.S.C. §360e",
        "agency": "FDA",
        "verticals": [("healthcare", 9, True)],
        "entities": [
            ("medical_device", {"sbom": "Include SBOM in 510(k) or PMA submissions", "patching": "Coordinated vulnerability disclosure policy required", "lifecycle": "Cybersecurity controls throughout device lifecycle"}),
        ],
    },
    {
        "regulation_id": "cms_telehealth_reimbursement_2024",
        "title": "CMS Telehealth Reimbursement Expansion Rule 2024",
        "type": "rule",
        "status": "final",
        "source": "cms",
        "summary": "CMS expands Medicare telehealth coverage permanently. Digital health platforms must meet new audio-visual standards and patient consent documentation requirements.",
        "published_date": "2024-01-01",
        "effective_date": "2024-01-01",
        "deadline_date": str(today + timedelta(days=75)),
        "complexity_score": 6,
        "impact_score": 9,
        "affected_entities": ["healthcare_provider", "health_insurer"],
        "keywords": ["telehealth", "CMS", "Medicare", "reimbursement", "digital health"],
        "citation": "42 CFR Part 410",
        "agency": "CMS",
        "verticals": [("healthcare", 10, True), ("insurance", 6, False)],
        "entities": [
            ("healthcare_provider", {"av_standards": "Meet CMS audio-visual quality standards", "consent": "Document patient consent for telehealth", "billing": "Use appropriate telehealth CPT codes"}),
        ],
    },
    # --- INSURANCE (2) ---
    {
        "regulation_id": "naic_cyber_model_law_2023",
        "title": "NAIC Insurance Data Security Model Law (#668)",
        "type": "rule",
        "status": "effective",
        "source": "state",
        "summary": "Insurers must implement comprehensive information security programs. Licensees with >10 employees must have written IS programs meeting NAIC standards.",
        "published_date": "2023-01-01",
        "effective_date": "2023-01-01",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 8,
        "affected_entities": ["insurer", "health_insurer"],
        "keywords": ["NAIC", "insurance", "cybersecurity", "data security", "Model Law 668"],
        "citation": "NAIC Model Law #668",
        "agency": "FTC",
        "verticals": [("insurance", 10, True), ("healthcare", 4, False)],
        "entities": [
            ("insurer", {"is_program": "Written information security program required", "risk_assessment": "Annual cybersecurity risk assessment", "incident_response": "72-hour breach notification to Commissioner"}),
        ],
    },
    {
        "regulation_id": "dol_fiduciary_rule_2024",
        "title": "DOL Retirement Security Rule (Fiduciary Rule 2024)",
        "type": "rule",
        "status": "final",
        "source": "federal_register",
        "summary": "Investment professionals providing retirement advice must act as fiduciaries. Expands who qualifies as a fiduciary under ERISA. Affects insurance annuity sales.",
        "published_date": "2024-04-23",
        "effective_date": "2024-09-23",
        "deadline_date": str(today + timedelta(days=120)),
        "complexity_score": 8,
        "impact_score": 8,
        "affected_entities": ["insurer", "investment_advisor", "broker_dealer"],
        "keywords": ["fiduciary", "DOL", "ERISA", "retirement", "annuity", "rollover"],
        "citation": "29 CFR Part 2510",
        "agency": "SEC",
        "verticals": [("insurance", 9, True), ("fintech", 5, False)],
        "entities": [
            ("insurer", {"fiduciary": "Act in best interest of retirement investors", "disclosure": "Disclose conflicts of interest", "annuity": "Apply fiduciary standard to annuity recommendations"}),
            ("investment_advisor", {"compliance": "Update policies for expanded fiduciary definition"}),
        ],
    },
    # --- SAAS (3) ---
    {
        "regulation_id": "gdpr_2018_eu_general",
        "title": "EU General Data Protection Regulation (GDPR)",
        "type": "rule",
        "status": "effective",
        "source": "international",
        "summary": "Comprehensive data privacy law for EU residents. Requirements for consent, data minimization, right to erasure, DPO appointment, and 72-hour breach notification.",
        "published_date": "2018-05-25",
        "effective_date": "2018-05-25",
        "deadline_date": None,
        "complexity_score": 9,
        "impact_score": 9,
        "affected_entities": ["saas_company", "fintech_lender", "healthcare_provider"],
        "keywords": ["GDPR", "EU", "privacy", "data protection", "consent", "DPO", "right to erasure"],
        "citation": "Regulation (EU) 2016/679",
        "agency": "FTC",
        "verticals": [("saas", 10, True), ("fintech", 8, True), ("healthcare", 7, True)],
        "entities": [
            ("saas_company", {"consent": "Lawful basis for all data processing", "dsar": "Respond to data subject requests within 30 days", "breach": "72-hour notification to supervisory authority", "dpo": "Appoint DPO if processing at large scale"}),
        ],
    },
    {
        "regulation_id": "soc2_aicpa_trust_services",
        "title": "AICPA SOC 2 Trust Services Criteria",
        "type": "guidance",
        "status": "effective",
        "source": "federal_register",
        "summary": "SOC 2 Type II certification requirements for SaaS companies. Covers Security, Availability, Processing Integrity, Confidentiality, and Privacy trust service criteria.",
        "published_date": "2022-01-01",
        "effective_date": "2022-01-01",
        "deadline_date": None,
        "complexity_score": 7,
        "impact_score": 7,
        "affected_entities": ["saas_company"],
        "keywords": ["SOC2", "AICPA", "trust services", "security", "audit", "compliance"],
        "citation": "AICPA TSP Section 100",
        "agency": "FTC",
        "verticals": [("saas", 9, True), ("fintech", 6, False), ("healthcare", 6, False)],
        "entities": [
            ("saas_company", {"security": "Implement CC6.1-CC9.2 common criteria", "availability": "Uptime SLAs and monitoring", "audit": "Annual Type II audit by licensed CPA firm"}),
        ],
    },
    {
        "regulation_id": "ftc_safeguards_rule_2023",
        "title": "FTC Safeguards Rule (Amended) - Non-Banking Financial Institutions",
        "type": "rule",
        "status": "effective",
        "source": "ftc",
        "summary": "Non-banking financial institutions must implement written information security programs. Covers SaaS companies providing financial services. Requires encryption, MFA, and incident response.",
        "published_date": "2023-06-09",
        "effective_date": "2023-06-09",
        "deadline_date": None,
        "complexity_score": 6,
        "impact_score": 7,
        "affected_entities": ["fintech_lender", "saas_company", "payment_processor"],
        "keywords": ["FTC", "Safeguards Rule", "GLBA", "information security", "encryption", "MFA"],
        "citation": "16 CFR Part 314",
        "agency": "FTC",
        "verticals": [("saas", 8, True), ("fintech", 9, True)],
        "entities": [
            ("saas_company", {"is_program": "Written information security program", "mfa": "MFA for accessing customer financial data", "encryption": "Encrypt data in transit and at rest", "incident": "Report incidents to FTC within 30 days"}),
            ("fintech_lender", {"same": "Full compliance with Safeguards Rule requirements"}),
        ],
    },
]


def insert_agencies(conn):
    cursor = conn.cursor()
    agency_ids = {}
    for name, abbr, website, api in AGENCIES:
        cursor.execute(
            "INSERT OR IGNORE INTO agencies (name, abbreviation, website, api_endpoint) VALUES (?,?,?,?)",
            (name, abbr, website, api),
        )
        cursor.execute("SELECT id FROM agencies WHERE abbreviation=?", (abbr,))
        agency_ids[abbr] = cursor.fetchone()[0]
    conn.commit()
    return agency_ids


def insert_sources(conn):
    cursor = conn.cursor()
    for name, abbr, url, api in SOURCES:
        cursor.execute(
            "INSERT OR IGNORE INTO regulatory_sources (name, abbreviation, url, api_endpoint, status) VALUES (?,?,?,?,'active')",
            (name, abbr, url, api),
        )
    conn.commit()


def insert_regulations(conn, agency_ids):
    cursor = conn.cursor()
    reg_counts = {"inserted": 0, "skipped": 0}

    for reg in REGULATIONS:
        agency_id = agency_ids.get(reg["agency"])
        try:
            cursor.execute(
                """INSERT OR IGNORE INTO regulations
                   (regulation_id, title, type, status, source, summary,
                    published_date, effective_date, deadline_date,
                    complexity_score, impact_score,
                    affected_entities, keywords, citation, agency_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    reg["regulation_id"],
                    reg["title"],
                    reg["type"],
                    reg["status"],
                    reg["source"],
                    reg["summary"],
                    reg.get("published_date"),
                    reg.get("effective_date"),
                    reg.get("deadline_date"),
                    reg["complexity_score"],
                    reg["impact_score"],
                    json.dumps(reg["affected_entities"]),
                    json.dumps(reg["keywords"]),
                    reg.get("citation"),
                    agency_id,
                ),
            )
            if cursor.rowcount == 0:
                reg_counts["skipped"] += 1
                continue

            reg_db_id = cursor.lastrowid
            reg_counts["inserted"] += 1

            # Verticals
            for vertical, score, critical in reg["verticals"]:
                cursor.execute(
                    "INSERT OR IGNORE INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (?,?,?,?)",
                    (reg_db_id, vertical, score, 1 if critical else 0),
                )

            # Entities
            for entity_type, requirements in reg.get("entities", []):
                cursor.execute(
                    "INSERT INTO regulation_entities (regulation_id, entity_type, compliance_requirements, deadline_date) VALUES (?,?,?,?)",
                    (reg_db_id, entity_type, json.dumps(requirements), reg.get("deadline_date")),
                )

            # Initial update record
            urgency = "critical" if reg.get("deadline_date") and (
                date.fromisoformat(reg["deadline_date"]) - today
            ).days <= 30 else "high" if reg["impact_score"] >= 8 else "medium"
            cursor.execute(
                "INSERT INTO regulation_updates (regulation_id, update_type, urgency) VALUES (?,?,?)",
                (reg_db_id, "new_regulation", urgency),
            )

        except Exception as e:
            print(f"  Warning: {reg['regulation_id']}: {e}")
            reg_counts["skipped"] += 1

    conn.commit()
    return reg_counts


def update_agency_counts(conn):
    conn.execute("""
        UPDATE agencies SET regulation_count = (
            SELECT COUNT(*) FROM regulations WHERE agency_id = agencies.id
        )
    """)
    conn.execute("""
        UPDATE regulatory_sources SET regulation_count = (
            SELECT COUNT(*) FROM regulations WHERE source = LOWER(regulatory_sources.abbreviation)
        ), last_sync = CURRENT_TIMESTAMP
    """)
    conn.commit()


def print_summary(conn):
    print("\n" + "=" * 60)
    print("LATTICE Database Seed Complete")
    print("=" * 60)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM regulations")
    print(f"  Total regulations : {cur.fetchone()[0]}")

    cur.execute("SELECT vertical, COUNT(*) as c FROM regulation_verticals GROUP BY vertical ORDER BY c DESC")
    print("\n  By vertical:")
    for row in cur.fetchall():
        print(f"    {row[0]:12s}  {row[1]}")

    cur.execute("SELECT status, COUNT(*) as c FROM regulations GROUP BY status ORDER BY c DESC")
    print("\n  By status:")
    for row in cur.fetchall():
        print(f"    {row[0]:12s}  {row[1]}")

    cur.execute("SELECT COUNT(*) FROM regulations WHERE deadline_date IS NOT NULL")
    print(f"\n  With deadlines   : {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM regulation_updates WHERE urgency='critical'")
    print(f"  Critical updates : {cur.fetchone()[0]}")
    print("=" * 60 + "\n")


def main():
    print(f"Seeding database: {DB_PATH}")
    conn = get_conn()
    init_schema(conn)
    agency_ids = insert_agencies(conn)
    print(f"  Inserted {len(agency_ids)} agencies")
    insert_sources(conn)
    print(f"  Inserted {len(SOURCES)} regulatory sources")
    counts = insert_regulations(conn, agency_ids)
    print(f"  Regulations: {counts['inserted']} inserted, {counts['skipped']} skipped")
    update_agency_counts(conn)
    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
