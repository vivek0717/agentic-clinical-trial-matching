from src.database import get_connection
ACTIVE_STATUSES = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
}


def normalize_text(value: object) -> str:
    """Return lowercase text for transparent simple comparisons."""
    return str(value or "").strip().lower()


def condition_is_related(patient_condition: str, trial_condition: str) -> bool:
    """
    Use conservative condition checks for an educational screening prototype.

    This is not a complete eligibility evaluation. It only determines whether
    the public trial condition appears related to the fictional profile.
    """
    patient_text = normalize_text(patient_condition)
    trial_text = normalize_text(trial_condition)

    if not patient_text or not trial_text:
        return False

    if patient_text in trial_text:
        return True

    if "type 2" in patient_text and (
        "type 2" in trial_text
        or "type ii" in trial_text
        or "diabetes mellitus, type 2" in trial_text
    ):
        return True

    return False


def match_patient_to_trial(patient: dict, trial: dict) -> dict:
    """
    Screen one synthetic profile against one public trial.

    This is a transparent, rules-based preliminary screen. It does not assess
    every protocol rule and never determines final trial eligibility.
    """
    reasons = []
    missing_info = []
    score = 0

    trial_status = normalize_text(trial.get("status")).upper()

    if trial_status not in ACTIVE_STATUSES:
        return {
            "decision": "likely_not_match",
            "score": 0,
            "reasons": ["Trial is not currently recruiting or active."],
            "missing_info": [],
        }

    patient_condition = patient.get("condition", patient.get("conditions", ""))
    trial_condition = trial.get("condition", "")

    if not condition_is_related(patient_condition, trial_condition):
        return {
            "decision": "likely_not_match",
            "score": 0,
            "reasons": [
                "Primary condition does not match the available trial condition."
            ],
            "missing_info": [],
        }

    reasons.append("Primary condition is related to the available trial condition.")
    score += 40

    patient_age = patient.get("age")
    min_age = trial.get("min_age_years")
    max_age = trial.get("max_age_years")

    if min_age is not None and patient_age < min_age:
        return {
            "decision": "likely_not_match",
            "score": score,
            "reasons": reasons + ["Age is below the available minimum age."],
            "missing_info": [],
        }

    if max_age is not None and patient_age > max_age:
        return {
            "decision": "likely_not_match",
            "score": score,
            "reasons": reasons + ["Age is above the available maximum age."],
            "missing_info": [],
        }

    if min_age is None and max_age is None:
        missing_info.append("Public age limits are unavailable for this trial.")
    else:
        reasons.append("Age is within the available trial range.")
        score += 30

    trial_sex = normalize_text(trial.get("sex"))

    if trial_sex in {"male", "female"}:
        patient_sex = normalize_text(patient.get("sex"))

        if patient_sex != trial_sex:
            return {
                "decision": "likely_not_match",
                "score": score,
                "reasons": reasons + [
                    "Available trial sex requirement does not match the profile."
                ],
                "missing_info": [],
            }

        reasons.append("Available trial sex requirement matches the profile.")
        score += 10
    else:
        reasons.append("No restrictive sex requirement is available in the record.")

    if not normalize_text(trial.get("criteria_text")):
        missing_info.append("Eligibility criteria text is unavailable.")
    else:
        reasons.append("Eligibility text is available for qualified human review.")
        score += 10

    if patient.get("hba1c") in (None, "", "Unknown"):
        missing_info.append("HbA1c is not provided in the synthetic profile.")

    if missing_info:
        decision = "needs_human_review"
    else:
        decision = "potential_match"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons,
        "missing_info": missing_info,
    }


def search_trials_by_condition(condition: str, limit: int = 50) -> list[dict]:
    """Return active public trial records whose condition contains a keyword."""
    query = """
        SELECT *
        FROM trials
        WHERE status IN ('RECRUITING', 'NOT_YET_RECRUITING', 'ACTIVE_NOT_RECRUITING')
          AND LOWER(condition) LIKE LOWER(?)
        ORDER BY nct_id
        LIMIT ?;
    """

    with get_connection() as connection:
        rows = connection.execute(query, (f"%{condition}%", limit)).fetchall()

    return [dict(row) for row in rows]


def find_potential_matches(patient: dict, limit: int = 5) -> list[dict]:
    """
    Find and rank public candidate trials for a synthetic profile.

    The function retrieves trials broadly using 'diabetes' for Type 2 diabetes
    profiles, then applies the stricter transparent matching rules above.
    """
    patient_condition = str(
        patient.get("condition", patient.get("conditions", ""))
    ).strip()

    search_term = "diabetes" if "diabetes" in patient_condition.lower() else patient_condition

    trials = search_trials_by_condition(search_term, limit=50)
    results = []

    for trial in trials:
        result = match_patient_to_trial(patient, trial)
        result["trial"] = trial
        results.append(result)

    ranked_results = sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked_results[:limit]