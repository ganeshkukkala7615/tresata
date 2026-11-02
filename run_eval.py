
"""Compare LLM extractions with gold answers after citation checking.
Reports per lease:
- Fields rejected by checker
- Fields wrong but accepted by checker
- Final calculator outcome

Writes eval_report.md.
"""

import json
import os
import sys

from leases import LEASES, lease_text
from checker import check_extraction
from calc import to_spec, compute


def normalize_value(name, value):
    """Normalize equivalent representations before gold comparison."""
    if name == "escalation" and isinstance(value, dict):
        if value.get("type") == "none":
            return {"type": "none"}

    return value


rows = []
total_fields = 0
rejected = 0
wrong_accepted = 0
correct = 0
detail = []

for lease in LEASES:
    path = f"outputs_llm/{lease['id']}.json"

    if not os.path.exists(path):
        rows.append(
            f"| {lease['id']} | missing output | - | - | - |"
        )
        continue

    with open(path, "r", encoding="utf-8") as file:
        extraction = json.load(file)

    if "_error" in extraction:
        rows.append(
            f"| {lease['id']} | extraction error | - | - | - |"
        )
        continue

    # Only evaluate fields with a value.
    fields = {
        key: value
        for key, value in extraction.items()
        if isinstance(value, dict) and "value" in value
    }

    checker_results = check_extraction(
        fields,
        lease_text(lease)
    )

    rejected_fields = [
        key
        for key, (passed, _) in checker_results.items()
        if not passed
    ]

    wrong_fields = []

    for key, gold_field in lease["gold"].items():
        if key in rejected_fields:
            continue

        if key not in fields:
            wrong_fields.append(key)
            continue

        model_value = normalize_value(
            key, fields[key].get("value")
        )
        gold_value = normalize_value(
            key, gold_field["value"]
        )

        if model_value != gold_value:
            wrong_fields.append(key)

    field_count = len(lease["gold"])
    rejected_count = len(rejected_fields)
    wrong_count = len(wrong_fields)
    correct_count = field_count - rejected_count - wrong_count

    total_fields += field_count
    rejected += rejected_count
    wrong_accepted += wrong_count
    correct += correct_count

    outcome = "-"

    # Calculate only when every expected field passes.
    if not rejected_fields and not wrong_fields:
        try:
            result = compute(to_spec(extraction), lease["human"])
            amount = result.get("liability", result.get("expense", ""))
            outcome = f"{result['status']} {amount}"
        except Exception as error:
            outcome = f"calculator error: {error}"

    for key in rejected_fields:
        detail.append(
            f"- {lease['id']}.{key}: "
            f"model={fields.get(key, {}).get('value')!r}; "
            f"gold={lease['gold'][key]['value']!r}; "
            f"CHECKER REJECTED"
        )

    for key in wrong_fields:
        detail.append(
            f"- {lease['id']}.{key}: "
            f"model={fields.get(key, {}).get('value')!r}; "
            f"gold={lease['gold'][key]['value']!r}; "
            f"ACCEPTED BY CHECKER BUT WRONG"
        )

    rows.append(
        f"| {lease['id']} | {correct_count}/{field_count} | "
        f"{', '.join(rejected_fields) or '-'} | "
        f"{', '.join(wrong_fields) or '-'} | {outcome} |"
    )


if not rows:
    sys.exit("No outputs found. Run extract.py first.")


report = [
    "# LLM extraction evaluation",
    (
        f"Fields: {total_fields}  "
        f"correct: {correct}  "
        f"rejected by checker: {rejected}  "
        f"wrong-but-accepted: {wrong_accepted}"
    ),
    "",
    "| Lease | Correct | Rejected by checker | Wrong but accepted | Calculator outcome |",
    "|---|---|---|---|---|",
] + rows + ["", "## Failures"] + (detail or ["None"])


with open("eval_report.md", "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\n".join(report))
print("\nSaved report to eval_report.md")
