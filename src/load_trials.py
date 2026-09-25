from pathlib import Path
import sqlite3

import pandas as pd

from src.database import DB_PATH, get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_CSV_FILE = BASE_DIR / "data_processed" / "trials_clean.csv"

DATABASE_COLUMNS = [
    "nct_id",
    "title",
    "condition",
    "status",
    "phases",
    "min_age_years",
    "max_age_years",
    "sex",
    "criteria_text",
    "source_url",
]


def prepare_trials_for_database(trials: pd.DataFrame) -> pd.DataFrame:
    """Select and rename clean CSV columns to match the SQLite trials table."""
    prepared = trials.copy()

    prepared = prepared.rename(columns={"conditions": "condition"})
    prepared = prepared.reindex(columns=DATABASE_COLUMNS)

    prepared["nct_id"] = prepared["nct_id"].astype(str).str.strip()
    prepared["title"] = prepared["title"].astype(str).str.strip()

    prepared = prepared.dropna(subset=["nct_id", "title"])
    prepared = prepared[
        (prepared["nct_id"] != "") & (prepared["title"] != "")
    ].copy()

    return prepared


def load_trials() -> int:
    """Replace public trial rows in SQLite using the cleaned CSV."""
    if not CLEAN_CSV_FILE.exists():
        raise FileNotFoundError(
            f"Clean trial CSV was not found: {CLEAN_CSV_FILE}\n"
            "Run `python src\\data_cleaning.py` first."
        )

    initialize_database()

    trials = pd.read_csv(CLEAN_CSV_FILE)
    prepared_trials = prepare_trials_for_database(trials)

    with get_connection() as connection:
        connection.execute("DELETE FROM trials;")

        prepared_trials.to_sql(
            "trials",
            connection,
            if_exists="append",
            index=False,
        )

        loaded_count = connection.execute(
            "SELECT COUNT(*) FROM trials;"
        ).fetchone()[0]

    return loaded_count


def main() -> None:
    loaded_count = load_trials()

    print(f"Database file: {DB_PATH}")
    print(f"Trials loaded into SQLite: {loaded_count}")


if __name__ == "__main__":
    main()