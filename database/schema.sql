PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS trials (
    nct_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    condition TEXT,
    status TEXT,
    phases TEXT,
    min_age_years INTEGER,
    max_age_years INTEGER,
    sex TEXT,
    criteria_text TEXT,
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 120),
    sex TEXT NOT NULL,
    state TEXT NOT NULL,
    conditions TEXT NOT NULL,
    medications TEXT,
    hba1c REAL,
    bmi REAL,
    is_synthetic INTEGER NOT NULL DEFAULT 1 CHECK (is_synthetic = 1)
);

CREATE TABLE IF NOT EXISTS match_results (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    nct_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (
        decision IN (
            'potential_match',
            'needs_human_review',
            'likely_not_match'
        )
    ),
    score REAL,
    evidence TEXT,
    missing_info TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id)
);

CREATE TABLE IF NOT EXISTS agent_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    step_name TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES match_results(match_id)
);

CREATE INDEX IF NOT EXISTS idx_trials_status
ON trials(status);

CREATE INDEX IF NOT EXISTS idx_match_results_patient
ON match_results(patient_id);