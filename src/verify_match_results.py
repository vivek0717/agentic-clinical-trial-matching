from database import get_connection


def main() -> None:
    with get_connection() as connection:
        match_count = connection.execute(
            "SELECT COUNT(*) FROM match_results;"
        ).fetchone()[0]

        audit_count = connection.execute(
            "SELECT COUNT(*) FROM agent_audit_logs;"
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT
                match_id,
                patient_id,
                nct_id,
                decision,
                score,
                created_at
            FROM match_results
            ORDER BY match_id;
            """
        ).fetchall()

    print(f"Saved match results: {match_count}")
    print(f"Saved audit logs: {audit_count}")

    print("\nMATCH RESULT PREVIEW")
    print("-" * 60)

    for row in rows:
        print(
            f"Match {row['match_id']}: "
            f"{row['patient_id']} -> {row['nct_id']} | "
            f"{row['decision']} | score={row['score']} | "
            f"created={row['created_at']}"
        )


if __name__ == "__main__":
    main()
    