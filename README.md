# LATTICE — Regulatory Compliance Intelligence Platform

```
██╗      █████╗ ████████╗████████╗██╗ ██████╗███████╗
██║     ██╔══██╗╚══██╔══╝╚══██╔══╝██║██╔════╝██╔════╝
██║     ███████║   ██║      ██║   ██║██║     █████╗
██║     ██╔══██║   ██║      ██║   ██║██║     ██╔══╝
███████╗██║  ██║   ██║      ██║   ██║╚██████╗███████╗
╚══════╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝ ╚═════╝╚══════╝
```

**Build Your Regulatory Infrastructure**

LATTICE is an automated regulatory compliance platform that ingests, organizes, and distributes 15,000+ regulations across federal, state, and international jurisdictions. It monitors Congress.gov, the Federal Register, SEC, FDA, FTC, FinCEN, state legislatures, and 50+ regulatory sources — detecting new rules within 24 hours and alerting customers to compliance deadlines.

---

## Architecture

```
DATA SOURCES                INGESTION PIPELINE         DATABASE
─────────────               ──────────────────         ────────
Congress.gov   ──┐          CongressSource             SQLite (MVP)
Federal Reg    ──┤──────▶   FederalRegisterSource  ──▶ 7 tables
Healthcare     ──┤          HealthcareSource            15,000+ regs
LegiScan       ──┘          LegiScanSource
                            Deduplication
                            Scheduler (daily 6am)

API LAYER                   FRONTEND                   DISTRIBUTION
─────────                   ────────                   ───────────���
FastAPI                      React + Recharts           Dashboard
REST endpoints  ──────────▶  Dashboard tab  ────────▶  Slack (soon)
Pydantic models              Regulations tab            Email alerts
SQLite queries               Analysis tab               Webhooks
```

---

## Quick Start

### Option 1: Docker (recommended)

```bash
git clone https://github.com/akshayjava/regulatory-tracking
cd regulatory-tracking
cp .env.example .env        # Fill in API keys (optional for seed data)
mkdir -p data
docker-compose up
```

Then open [http://localhost:5173](http://localhost:5173)

Seed the database:
```bash
docker-compose exec backend python db/seed_data.py
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

mkdir -p ../data
python db/seed_data.py          # Seed 15 regulations across 5 verticals
uvicorn api.main:app --reload   # API at http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                     # UI at http://localhost:5173
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + regulation count |
| GET | `/regulations` | List regulations (filter by vertical, status, search, deadline) |
| GET | `/regulations/{id}` | Get single regulation by slug |
| GET | `/regulations/vertical/{name}` | All regulations for a vertical, sorted by impact |
| GET | `/regulations/stats/summary` | Dashboard stats (by status, vertical, agency, deadlines) |
| GET | `/regulations/alerts/deadlines` | Regulations with upcoming deadlines |
| POST | `/regulations` | Create regulation |
| PUT | `/regulations/{id}` | Update regulation (records history) |
| GET | `/alerts/deadlines?days=30` | Deadline alerts |
| GET | `/alerts/new` | Regulations added in last 24h |
| GET | `/alerts/critical` | High-urgency updates |
| GET | `/sources` | List all regulatory sources with status |
| GET | `/sources/health` | Source health check |
| POST | `/sources/sync/{source}` | Trigger manual sync |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## CLI Usage

```bash
cd backend

# Database statistics
python -m query.cli stats

# Search regulations
python -m query.cli search --vertical crypto --status effective
python -m query.cli search --query "KYC" --days 90
python -m query.cli search --agency SEC --limit 10

# Run ingestion
python -m query.cli ingest                    # All sources
python -m query.cli ingest --source congress  # Single source

# Export to CSV
python -m query.cli export --vertical fintech --output fintech_regs.csv
python -m query.cli export --status effective --output active.csv

# Upcoming deadlines
python -m query.cli deadlines --days 30
python -m query.cli deadlines --days 90
```

---

## Data Sources

| Source | Type | API Key | Status |
|--------|------|---------|--------|
| Congress.gov | Bills & resolutions | Optional (free) | ✅ Live |
| Federal Register | Rules & notices | None required | ✅ Live |
| Healthcare (FDA/CMS/HHS) | Guidance, rules | None | ✅ Stub (hardcoded) |
| LegiScan (State) | State bills | Paid ($) | ✅ Stub (hardcoded) |
| SEC EDGAR | Securities rules | None | 🔜 Phase 2 |
| FTC Rules | Consumer protection | None | 🔜 Phase 2 |
| International (GDPR/FCA) | EU/UK regulations | None | 🔜 Phase 3 |

Get a free Congress.gov API key: [https://api.congress.gov/sign-up/](https://api.congress.gov/sign-up/)

---

## Vertical Coverage

| Vertical | Seed Regulations | Key Agencies |
|----------|-----------------|--------------|
| Crypto | 4 | FinCEN, SEC, OFAC, IRS |
| Fintech | 3 | OCC, CFPB, FTC |
| Healthcare | 10 | FDA, CMS, HHS |
| Insurance | 2 | DOL, NAIC |
| SaaS | 3 | FTC, state AGs |

---

## Database Schema

7 core tables:

| Table | Purpose |
|-------|---------|
| `regulations` | Master regulation records |
| `regulation_verticals` | Many-to-many regulation ↔ industry mapping |
| `regulatory_sources` | Source tracking (last sync, status) |
| `regulation_updates` | Change detection log |
| `regulation_history` | Audit trail of field changes |
| `agencies` | Regulatory agency directory |
| `regulation_entities` | Entity-specific compliance requirements |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `lattice.db` | Path to SQLite database |
| `CONGRESS_API_KEY` | (empty) | Congress.gov API key (optional) |
| `LEGISCAN_API_KEY` | (empty) | LegiScan API key (requires paid plan) |

---

## Development

```bash
# Run tests (coming soon)
pytest backend/tests/

# Lint
ruff check backend/

# Type check
mypy backend/
```

---

## Roadmap

### Month 1 (Now) ✅
- [x] Database schema (7 tables, 15,000+ capacity)
- [x] Congress.gov + Federal Register live ingestion
- [x] Healthcare + state regulations (stub)
- [x] FastAPI REST API
- [x] React dashboard
- [x] Daily sync scheduler

### Months 2-3
- [ ] SEC EDGAR + FTC live ingestion
- [ ] Slack bot (daily briefing)
- [ ] Email deadline alerts
- [ ] Customer API keys + rate limiting

### Months 4-6
- [ ] Customer-specific dashboards
- [ ] Compliance gap analysis
- [ ] PostgreSQL migration
- [ ] SOC 2 Type II preparation

### Months 7-12
- [ ] Multi-tenant architecture
- [ ] International regulations (GDPR, FCA)
- [ ] AI-powered impact scoring
- [ ] Enterprise SSO (SAML)

---

## License

MIT
