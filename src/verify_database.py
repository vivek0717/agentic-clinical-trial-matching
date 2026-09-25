from database import get_recruiting_trial_preview, get_trial_summary


def main() -> None:
    summary = get_trial_summary()

    print("DATABASE SUMMARY")
    print("-" * 50)
    print(f"Total trials: {summary['total_trials']}")
    print(
        "Recruiting / not yet recruiting / active-not-recruiting: "
        f"{summary['recruiting_or_active_trials']}"
    )
    print(
        "Trials with available age information: "
        f"{summary['trials_with_age_information']}"
    )

    preview = get_recruiting_trial_preview(limit=10)

    print("\nRECRUITING TRIAL PREVIEW")
    print("-" * 50)

    if not preview:
        print("No recruiting or active candidate trials were found in this sample.")
        return

    for trial in preview:
        print(f"\nNCT ID: {trial['nct_id']}")
        print(f"Title: {trial['title']}")
        print(f"Status: {trial['status']}")
        print(f"Condition: {trial['condition']}")
        print(
            "Age range: "
            f"{trial['min_age_years'] or 'Not specified'}"
            " to "
            f"{trial['max_age_years'] or 'Not specified'}"
        )
        print(f"Source: {trial['source_url']}")


if __name__ == "__main__":
    main()