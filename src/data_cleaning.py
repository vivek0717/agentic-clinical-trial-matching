from pathlib import Path
import json
import re

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data_raw" / "type2_diabetes_trials_raw.json"
PROCESSED_DIR = BASE_DIR / "data_processed"
RAW_CSV_FILE = PROCESSED_DIR / "trials_raw.csv"
CLEAN_CSV_FILE = PROCESSED_DIR / "trials_clean.csv"


def get_text_list(values: list[str] | None) -> str:
    """Join a list safely into one semicolon-separated string."""
    return "; ".join(values or [])


def extract_trial_rows(studies: list[dict]) -> list[dict]:
    """Extract required fields from ClinicalTrials.gov study records."""
    rows = []

    for study in studies:
        protocol = study.get("protocolSection", {})

        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        conditions = protocol.get("conditionsModule", {})
        eligibility = protocol.get("eligibilityModule", {})

        nct_id = identification.get("nctId")

        rows.append(
            {
                "nct_id": nct_id,
                "title": identification.get("briefTitle"),
                "status": status.get("overallStatus"),
                "conditions": get_text_list(conditions.get("conditions")),
                "phases": get_text_list(design.get("phases")),
                "minimum_age": eligibility.get("minimumAge"),
                "maximum_age": eligibility.get("maximumAge"),
                "sex": eligibility.get("sex"),
                "criteria_text": eligibility.get("eligibilityCriteria"),
                "source_url": (
                    f"https://clinicaltrials.gov/study/{nct_id}"
                    if nct_id
                    else None
                ),
            }
        )

    return rows


def age_to_years(value: object) -> int | None:
    """Convert a value such as '18 Years' to 18; return None if unavailable."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    match = re.match(r"^(\d+)\s+year", text, flags=re.IGNORECASE)

    if match:
        return int(match.group(1))

    return None


def clean_trials(trials_raw: pd.DataFrame) -> pd.DataFrame:
    """Create a SQLite-ready trial dataset without inventing missing values."""
    trials_clean = trials_raw.copy()

    rows_before = len(trials_clean)

    trials_clean = trials_clean.drop_duplicates(subset="nct_id")
    duplicates_removed = rows_before - len(trials_clean)

    trials_clean = trials_clean.dropna(subset=["nct_id", "title"])
    trials_clean["nct_id"] = trials_clean["nct_id"].astype(str).str.strip()
    trials_clean["title"] = trials_clean["title"].astype(str).str.strip()

    trials_clean = trials_clean[
        (trials_clean["nct_id"] != "") & (trials_clean["title"] != "")
    ].copy()

    trials_clean["status"] = (
        trials_clean["status"]
        .fillna("UNKNOWN")
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace("-", "_", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    trials_clean["min_age_years"] = trials_clean["minimum_age"].apply(age_to_years)
    trials_clean["max_age_years"] = trials_clean["maximum_age"].apply(age_to_years)

    trials_clean["criteria_text"] = trials_clean["criteria_text"].fillna("").astype(str)
    missing_criteria = (trials_clean["criteria_text"].str.strip() == "").sum()

    trials_clean.attrs["duplicates_removed"] = duplicates_removed
    trials_clean.attrs["missing_criteria"] = int(missing_criteria)

    return trials_clean


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw trial file was not found: {RAW_FILE}\n"
            "Run `python src\\data_download.py` first."
        )

    PROCESSED_DIR.mkdir(exist_ok=True)

    with RAW_FILE.open("r", encoding="utf-8") as file:
        studies = json.load(file)

    rows = extract_trial_rows(studies)
    trials_raw = pd.DataFrame(rows)
    trials_raw.to_csv(RAW_CSV_FILE, index=False)

    trials_clean = clean_trials(trials_raw)
    trials_clean.to_csv(CLEAN_CSV_FILE, index=False)

    print(f"Raw studies read: {len(studies)}")
    print(f"Raw CSV rows created: {len(trials_raw)}")
    print(f"Clean CSV rows created: {len(trials_clean)}")
    print(f"Duplicates removed: {trials_clean.attrs['duplicates_removed']}")
    print(f"Rows with missing eligibility criteria: {trials_clean.attrs['missing_criteria']}")
    print(f"Raw CSV saved to: {RAW_CSV_FILE}")
    print(f"Clean CSV saved to: {CLEAN_CSV_FILE}")

    print("\nClean-data preview:")
    print(
        trials_clean[
            [
                "nct_id",
                "status",
                "minimum_age",
                "min_age_years",
                "maximum_age",
                "max_age_years",
            ]
        ].head(5)
    )


if __name__ == "__main__":
    main()