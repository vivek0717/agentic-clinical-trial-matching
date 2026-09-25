from pathlib import Path
import json

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data_raw"
OUTPUT_FILE = RAW_DATA_DIR / "type2_diabetes_trials_raw.json"

API_URL = "https://clinicaltrials.gov/api/v2/studies"


def download_trials(page_size: int = 10) -> list[dict]:
    """Download public Type 2 diabetes trial records from ClinicalTrials.gov."""
    params = {
        "query.cond": "Type 2 Diabetes",
        "pageSize": page_size,
        "format": "json",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    return payload.get("studies", [])


def main() -> None:
    RAW_DATA_DIR.mkdir(exist_ok=True)

    studies = download_trials(page_size=100)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(studies, file, indent=2)

    print(f"Trials downloaded: {len(studies)}")
    print(f"Raw data saved to: {OUTPUT_FILE}")

    if studies:
        print("Top-level fields in the first study:")
        print(list(studies[0].keys()))


if __name__ == "__main__":
    main()