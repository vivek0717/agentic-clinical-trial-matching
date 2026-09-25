from pathlib import Path

import pandas as pd

from src.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
PATIENTS_CSV_FILE = BASE_DIR / "data_processed" / "mock_patients.csv"

PATIENT_COLUMNS = [
    "patient_id",
    "age",
    "sex",
    "state",
    "conditions",
    "medications",
    "hba1c",
    "bmi",
    "is_synthetic",
]


def prepare_patients_for_database(patients: pd.DataFrame) -> pd.DataFrame:
    """Validate basic structure and retain safe synthetic patient fields only."""
    prepared = patients.reindex(columns=PATIENT_COLUMNS).copy()

    prepared["patient_id"] = prepared["patient_id"].astype(str).str.strip()
    prepared["age"] = pd.to_numeric(prepared["age"], errors="coerce")
    prepared["is_synthetic"] = pd.to_numeric(
        prepared["is_synthetic"], errors="coerce"
    ).fillna(0).astype(int)

    if not (prepared["is_synthetic"] == 1).all():
        raise ValueError(
            "All records must be marked is_synthetic = 1. "
            "Do not load real patient data."
        )

    required_columns = ["patient_id", "age", "sex", "state", "conditions"]

    if prepared[required_columns].isna().any().any():
        raise ValueError("Synthetic patient CSV has missing required values.")

    if prepared["patient_id"].duplicated().any():
        raise ValueError("Synthetic patient IDs must be unique.")

    if not prepared["age"].between(18, 120).all():
        raise ValueError("Each synthetic patient age must be between 18 and 120.")

    prepared["age"] = prepared["age"].astype(int)

    return prepared


def load_patients() -> int:
    """Replace synthetic patient test profiles in SQLite."""
    if not PATIENTS_CSV_FILE.exists():
        raise FileNotFoundError(
            f"Synthetic patient CSV was not found: {PATIENTS_CSV_FILE}"
        )

    initialize_database()

    patients = pd.read_csv(PATIENTS_CSV_FILE)
    prepared_patients = prepare_patients_for_database(patients)

    with get_connection() as connection:
        connection.execute("DELETE FROM patients;")

        prepared_patients.to_sql(
            "patients",
            connection,
            if_exists="append",
            index=False,
        )

        loaded_count = connection.execute(
            "SELECT COUNT(*) FROM patients;"
        ).fetchone()[0]

    return loaded_count


def main() -> None:
    loaded_count = load_patients()
    print(f"Synthetic patients loaded into SQLite: {loaded_count}")


if __name__ == "__main__":
    main()