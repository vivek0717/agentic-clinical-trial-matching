from flask import Flask, render_template, request

from src.matching import find_potential_matches
from src.validation import validate_patient_input

app = Flask(__name__)

SAFETY_DISCLAIMER = (
    "Educational portfolio prototype only. Do not enter real patient information. "
    "This application does not provide medical advice, diagnosis, treatment "
    "recommendations, or final clinical-trial eligibility decisions."
)


@app.route("/")
def home():
    return render_template(
        "index.html",
        disclaimer=SAFETY_DISCLAIMER,
        patient={},
        errors=[],
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        disclaimer=SAFETY_DISCLAIMER,
    )


@app.route("/match", methods=["POST"])
def match():
    age_text = request.form.get("age", "").strip()

    try:
        age = int(age_text)
    except ValueError:
        age = None

    hba1c_text = request.form.get("hba1c", "").strip()

    try:
        hba1c = float(hba1c_text) if hba1c_text else None
    except ValueError:
        hba1c = None

    patient = {
        "patient_id": request.form.get("patient_id", "").strip(),
        "age": age,
        "sex": request.form.get("sex", "").strip(),
        "state": request.form.get("state", "").strip(),
        "condition": request.form.get("condition", "").strip(),
        "medications": request.form.get("medications", "").strip(),
        "hba1c": hba1c,
        "is_synthetic": 1,
    }

    errors = validate_patient_input(patient)

    if errors:
        return (
            render_template(
                "index.html",
                disclaimer=SAFETY_DISCLAIMER,
                patient=patient,
                errors=errors,
            ),
            400,
        )

    results = find_potential_matches(patient, limit=5)

    return render_template(
        "results.html",
        disclaimer=SAFETY_DISCLAIMER,
        patient=patient,
        results=results,
    )


if __name__ == "__main__":
    app.run(debug=True)