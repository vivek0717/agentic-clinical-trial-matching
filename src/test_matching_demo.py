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
        print("INPUT ERRORS")
        for error in errors:
            print(f"- {error}")
        return

    results = find_potential_matches(patient, limit=5)

    print("MEDI TRIAL NAVIGATOR — SYNTHETIC PROFILE DEMO")
    print("-" * 60)
    print(
        f"Profile: {patient['patient_id']} | "
        f"Age: {patient['age']} | "
        f"Condition: {patient['condition']}"
    )

    if not results:
        print("\nNo candidate public trials were found.")
        return

    for number, item in enumerate(results, start=1):
        trial = item["trial"]

        print(f"\n{number}. {trial['title']}")
        print(f"NCT ID: {trial['nct_id']}")
        print(f"Status: {trial['status']}")
        print(f"Decision: {item['decision']}")
        print(f"Score: {item['score']}")

        print("Reasons:")
        for reason in item["reasons"]:
            print(f"- {reason}")

        if item["missing_info"]:
            print("Missing information:")
            for missing_item in item["missing_info"]:
                print(f"- {missing_item}")

        print(f"Public record: {trial['source_url']}")

    print(
        "\nSafety note: Educational prototype only. Results do not provide "
        "medical advice or determine clinical-trial eligibility."
    )


if __name__ == "__main__":
    main()