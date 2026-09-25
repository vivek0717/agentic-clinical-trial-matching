def validate_patient_input(patient: dict) -> list[str]:
    """
    Validate a fictional patient profile before trial screening.

    This educational prototype accepts synthetic data only and does not
    provide medical advice or final clinical-trial eligibility decisions.
    """
    errors = []

    patient_id = str(patient.get("patient_id", "")).strip()
    if not patient_id:
        errors.append("Synthetic patient ID is required.")
    elif not patient_id.upper().startswith("SYN"):
        errors.append("Patient ID must be a synthetic ID beginning with 'SYN'.")

    age = patient.get("age")
    if isinstance(age, bool) or not isinstance(age, int) or not 18 <= age <= 120:
        errors.append("Age must be a whole number from 18 to 120.")

    sex = str(patient.get("sex", "")).strip()
    if not sex:
        errors.append("Sex is required.")

    state = str(patient.get("state", "")).strip()
    if not state:
        errors.append("State is required.")

    condition = str(
        patient.get("condition", patient.get("conditions", ""))
    ).strip()
    if not condition:
        errors.append("Primary condition is required.")

    is_synthetic = patient.get("is_synthetic", 1)
    if is_synthetic not in (1, True, "1"):
        errors.append("Only synthetic patient profiles are allowed.")

    return errors