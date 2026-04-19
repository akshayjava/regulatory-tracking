-- LATTICE Regulatory Compliance Platform
-- SQLite Database Schema

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ============================================================
-- 1. AGENCIES
-- ============================================================
CREATE TABLE IF NOT EXISTS agencies (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    abbreviation      TEXT NOT NULL UNIQUE,
    website           TEXT,
    api_endpoint      TEXT,
    last_sync         DATETIME,
    regulation_count  INTEGER DEFAULT 0,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agencies_abbreviation ON agencies(abbreviation);

-- ============================================================
-- 2. REGULATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS regulations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id     TEXT NOT NULL UNIQUE,
    title             TEXT NOT NULL,
    description       TEXT,
    full_text         TEXT,
    summary           TEXT,
    type              TEXT NOT NULL CHECK(type IN ('bill','rule','guidance','enforcement','notice','order')),
    status            TEXT NOT NULL CHECK(status IN ('proposed','final','effective','withdrawn','superseded')),
    source            TEXT NOT NULL CHECK(source IN ('congress','federal_register','sec','fda','ftc','fincen','cms','hhs','ofac','irs','state','international')),
    published_date    DATE,
    effective_date    DATE,
    deadline_date     DATE,
    complexity_score  INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    impact_score      INTEGER CHECK(impact_score BETWEEN 1 AND 10),
    affected_entities TEXT DEFAULT '[]',
    keywords          TEXT DEFAULT '[]',
    citation          TEXT,
    agency_id         INTEGER REFERENCES agencies(id) ON DELETE SET NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulations_status    ON regulations(status);
CREATE INDEX IF NOT EXISTS idx_regulations_deadline  ON regulations(deadline_date);
CREATE INDEX IF NOT EXISTS idx_regulations_source    ON regulations(source);
CREATE INDEX IF NOT EXISTS idx_regulations_impact    ON regulations(impact_score DESC);
CREATE INDEX IF NOT EXISTS idx_regulations_published ON regulations(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_regulations_agency    ON regulations(agency_id);

-- ============================================================
-- 3. REGULATION VERTICALS  (many-to-many)
-- ============================================================
CREATE TABLE IF NOT EXISTS regulation_verticals (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id    INTEGER NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    vertical         TEXT NOT NULL CHECK(vertical IN ('crypto','fintech','healthcare','insurance','saas')),
    relevance_score  INTEGER CHECK(relevance_score BETWEEN 1 AND 10),
    is_critical      INTEGER DEFAULT 0,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(regulation_id, vertical)
);

CREATE INDEX IF NOT EXISTS idx_reg_verticals_vertical ON regulation_verticals(vertical);
CREATE INDEX IF NOT EXISTS idx_reg_verticals_reg_id   ON regulation_verticals(regulation_id);

-- ============================================================
-- 4. REGULATORY SOURCES
-- ============================================================
CREATE TABLE IF NOT EXISTS regulatory_sources (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    abbreviation     TEXT NOT NULL UNIQUE,
    url              TEXT,
    api_endpoint     TEXT,
    last_sync        DATETIME,
    next_sync        DATETIME,
    status           TEXT DEFAULT 'active' CHECK(status IN ('active','error','paused','pending')),
    regulation_count INTEGER DEFAULT 0,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. REGULATION UPDATES
-- ============================================================
CREATE TABLE IF NOT EXISTS regulation_updates (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id INTEGER NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    update_type   TEXT NOT NULL CHECK(update_type IN ('new_regulation','rule_finalized','deadline_approaching','status_change','text_updated')),
    detected_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    notified_at   DATETIME,
    urgency       TEXT DEFAULT 'medium' CHECK(urgency IN ('critical','high','medium','low')),
    details       TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_updates_urgency  ON regulation_updates(urgency);
CREATE INDEX IF NOT EXISTS idx_updates_detected ON regulation_updates(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_updates_reg_id   ON regulation_updates(regulation_id);

-- ============================================================
-- 6. REGULATION HISTORY
-- ============================================================
CREATE TABLE IF NOT EXISTS regulation_history (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id    INTEGER NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    field_changed    TEXT NOT NULL,
    old_value        TEXT,
    new_value        TEXT,
    changed_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_detected  TEXT
);

CREATE INDEX IF NOT EXISTS idx_history_reg_id  ON regulation_history(regulation_id);
CREATE INDEX IF NOT EXISTS idx_history_changed ON regulation_history(changed_at DESC);

-- ============================================================
-- 7. REGULATION ENTITIES
-- ============================================================
CREATE TABLE IF NOT EXISTS regulation_entities (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id           INTEGER NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    entity_type             TEXT NOT NULL CHECK(entity_type IN ('bank','crypto_exchange','crypto_custodian','defi_protocol','fintech_lender','payment_processor','healthcare_provider','health_insurer','medical_device','insurer','saas_company','broker_dealer','investment_advisor')),
    compliance_requirements TEXT DEFAULT '{}',
    deadline_date           DATE,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entities_reg_id ON regulation_entities(regulation_id);
CREATE INDEX IF NOT EXISTS idx_entities_type   ON regulation_entities(entity_type);

-- ============================================================
-- 8. REGULATION ANNOTATIONS  (AI-generated plain-language summaries)
-- ============================================================
CREATE TABLE IF NOT EXISTS regulation_annotations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id    INTEGER NOT NULL REFERENCES regulations(id) ON DELETE CASCADE UNIQUE,
    annotation       TEXT NOT NULL,
    model_used       TEXT,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_annotations_reg_id ON regulation_annotations(regulation_id);

-- ============================================================
-- TRIGGER: auto-update regulations.updated_at
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_regulations_updated_at
    AFTER UPDATE ON regulations
    FOR EACH ROW
BEGIN
    UPDATE regulations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
