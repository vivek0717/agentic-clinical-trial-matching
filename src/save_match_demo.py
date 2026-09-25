from database import save_audit_log, save_match_result
from matching import find_potential_matches
from validation import validate_patient_input


def main() -> None:
    patient = {
        "patient_id": "SYN001",
        "age": 58,
        "sex": "Female",
        "state": "New Jersey",
        "condition": "Type 2 diabetes",
        "medications": "Metformin; Lisinopril",
        "hba1c": 8.2,
        "is_synthetic": 1,
    }

    errors = validate_patient_input(patient)

    if errors:
        print("Input validation failed:")
        for error in errors:
            print(f"- {error}")
        return

    matches = find_potential_matches(patient, limit=5)

    if not matches:
        print("No candidate trials were found to save.")
        return

    for item in matches:
        trial = item["trial"]

        match_id = save_match_result(
            patient_id=patient["patient_id"],
            nct_id=trial["nct_id"],
            decision=item["decision"],
            score=item["score"],
            reasons=item["reasons"],
            missing_info=item["missing_info"],
        )

        save_audit_log(
            match_id=match_id,
            step_name="rules_based_matching_completed",
            input_summary=(
                f"Synthetic profile {patient['patient_id']}; "
                f"age={patient['age']}; "
                f"condition={patient['condition']}"
            ),
            output_summary=(
                f"decision={item['decision']}; "
                f"score={item['score']}; "
                f"trial={trial['nct_id']}"
            ),
        )

        print(
            f"Saved match {match_id}: "
            f"{patient['patient_id']} -> {trial['nct_id']} "
            f"({item['decision']}, score={item['score']})"
        )

    print("\nSaved rules-based match results and audit logs.")
    print(
        "Safety note: Stored results are educational screening artifacts only; "
        "they are not medical decisions."
    )


if __name__ == "__main__":
    main()