from pathlib import Path
import sqlite3
from pathlib import Path
import json
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "meditrial.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection that provides rows by column name."""
    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def initialize_database() -> None:
    """Create all project tables and indexes if they do not already exist."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file was not found: {SCHEMA_PATH}")

    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    with get_connection() as connection:
        connection.executescript(schema_sql)

    print(f"Database initialized: {DB_PATH}")

def get_trial_summary() -> dict:
    """Return basic trial counts for database verification."""
    with get_connection() as connection:
        total_trials = connection.execute(
            "SELECT COUNT(*) FROM trials;"
        ).fetchone()[0]

        recruiting_trials = connection.execute(
            """
            SELECT COUNT(*)
            FROM trials
            WHERE status IN ('RECRUITING', 'NOT_YET_RECRUITING', 'ACTIVE_NOT_RECRUITING');
            """
        ).fetchone()[0]

        trials_with_age_ranges = connection.execute(
            """
            SELECT COUNT(*)
            FROM trials
            WHERE min_age_years IS NOT NULL OR max_age_years IS NOT NULL;
            """
        ).fetchone()[0]

    return {
        "total_trials": total_trials,
        "recruiting_or_active_trials": recruiting_trials,
        "trials_with_age_information": trials_with_age_ranges,
    }


def get_recruiting_trial_preview(limit: int = 10) -> list[dict]:
    """Return a small, safe preview of candidate public trial records."""
    query = """
        SELECT
            nct_id,
            title,
            status,
            condition,
            min_age_years,
            max_age_years,
            source_url
        FROM trials
        WHERE status IN ('RECRUITING', 'NOT_YET_RECRUITING', 'ACTIVE_NOT_RECRUITING')
        ORDER BY nct_id
        LIMIT ?;
    """

    with get_connection() as connection:
        rows = connection.execute(query, (limit,)).fetchall()

    return [dict(row) for row in rows]
import json


def save_match_result(
    patient_id: str,
    nct_id: str,
    decision: str,
    score: float,
    reasons: list[str],
    missing_info: list[str],
) -> int:
    """
    Save a rules-based screening result for a synthetic profile.

    The stored record is an educational screening artifact only. It is not a
    medical conclusion or a final clinical-trial enrollment decision.
    """
    evidence = json.dumps(reasons)
    missing_info_json = json.dumps(missing_info)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO match_results (
                patient_id,
                nct_id,
                decision,
                score,
                evidence,
                missing_info
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                patient_id,
                nct_id,
                decision,
                score,
                evidence,
                missing_info_json,
            ),
        )

        match_id = cursor.lastrowid

    return match_id


def save_audit_log(
    match_id: int,
    step_name: str,
    input_summary: str,
    output_summary: str,
) -> None:
    """Save a concise audit trail for a matching step."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO agent_audit_logs (
                match_id,
                step_name,
                input_summary,
                output_summary
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                match_id,
                step_name,
                input_summary,
                output_summary,
            ),
        )
if __name__ == "__main__":
    initialize_database()