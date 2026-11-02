
"""Deterministic citation checker. No LLM involved."""

import re


def norm(s):
    s = str(s)
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def _nums(text):
    return {
        float(x.replace(",", ""))
        for x in re.findall(r"\d[\d,]*\.?\d*", str(text))
        if x.strip(",")
    }


def _value_numbers(name, value):
    if name == "escalation" and isinstance(value, dict):
        pct = value.get("pct")
        if pct is None:
            return []
        try:
            return [float(pct)]
        except (TypeError, ValueError):
            return []

    if name == "base_term_months":
        return []

    if name == "commencement_date":
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return [float(value[:4])]
        return []

    if name in ("payment_amount", "free_rent_months"):
        if value is None:
            return []
        try:
            return [float(value)]
        except (TypeError, ValueError):
            return []

    return []


def _base_term_matches(value, quote):
    try:
        months = float(value)
    except (TypeError, ValueError):
        return False

    numbers = _nums(quote)

    # Direct month value, e.g. 60 months.
    if months in numbers and re.search(r"\bmonths?\b", norm(quote)):
        return True

    # Convert years to months, e.g. 10 years = 120 months.
    if months % 12 == 0:
        years = months / 12
        if years in numbers and re.search(r"\byears?\b", norm(quote)):
            return True

    return False


def check_field(name, field, source):
    value = field.get("value")
    quote = field.get("quote")

    # not_stated may have no quote, or an exact quote explaining absence.
    if value == "not_stated":
        if quote and norm(quote) not in norm(source):
            return False, "quote is not in the source text"
        return True, "not_stated"

    if not quote:
        return False, "no quote supplied"

    if norm(quote) not in norm(source):
        return False, "quote is not in the source text"

    if name == "base_term_months":
        if not _base_term_matches(value, quote):
            return False, f"term value {value!r} does not match its quoted months/years"
        return True, "ok"

    quote_numbers = _nums(quote)

    for number in _value_numbers(name, value):
        if number not in quote_numbers:
            return False, f"value {number:g} does not appear in its quote"

    return True, "ok"


def check_extraction(extraction, source):
    return {
        key: check_field(key, field, source)
        for key, field in extraction.items()
    }


def all_ok(results):
    return all(ok for ok, _ in results.values())
