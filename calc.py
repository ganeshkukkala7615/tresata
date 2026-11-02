"""Deterministic IFRS 16 / Ind AS 116 lessee calculator. No LLM anywhere.
Conventions (stated so an auditor can challenge them):
 - discount rate is an annual effective rate, supplied by the accountant (IBR)
 - cash flow at month-offset t is discounted by (1+r)^(t/12)
 - index-linked (CPI) rent is measured at the commencement-date level, no forecasting (IFRS 16.27(b), 28)
 - turnover rent is variable and excluded from the liability (IFRS 16.27)
 - 'greater of fixed % or CPI': the fixed % floor is treated as in-substance fixed and flagged
 - ROU asset = liability (no initial direct costs, incentives or prepayments modelled)
"""
FREQ = {"monthly": 1, "quarterly": 3, "annual": 12}
CRITICAL = ["base_term_months", "payment_amount", "frequency", "timing", "escalation"]
LOW_VALUE_LIMIT = 5000   # USD, new-asset basis (IFRS 16 BC100 illustration)

def to_spec(extraction):
    return {k: f["value"] for k, f in extraction.items()}

def cash_flows(spec, term_months):
    f = FREQ[spec["frequency"]]
    esc = spec["escalation"]
    free = spec["free_rent_months"] if spec["free_rent_months"] != "not_stated" else 0
    flows, s = [], 0
    while s < term_months:
        amt = float(spec["payment_amount"])
        if esc["type"] in ("fixed_pct", "greater_of"):
            amt *= (1 + esc["pct"] / 100) ** (s // esc["interval_months"])
        if s < free:
            amt = 0.0
        t = s if spec["timing"] == "advance" else s + f
        flows.append((t, amt))
        s += f
    return flows

def compute(spec, human):
    """Returns dict: status, flags, liability, schedule, ... Never raises on a spec the human approved."""
    flags = []
    missing = [k for k in CRITICAL if spec.get(k) == "not_stated"]
    if missing:
        return {"status": "needs_human", "reason": f"lease is silent / not extracted: {missing}", "flags": flags}
    term, r = human["term_months"], human["rate"]
    flows = cash_flows(spec, term)
    total_paid = sum(a for _, a in flows)
    if term <= 12:
        return {"status": "exempt_short_term", "expense": round(total_paid, 2), "flags": flags}
    if human.get("asset_value_new") is not None and human["asset_value_new"] <= LOW_VALUE_LIMIT:
        return {"status": "exempt_low_value", "expense": round(total_paid, 2), "flags": flags}
    if spec["escalation"]["type"] == "cpi":
        flags.append("CPI-linked: liability measured at current index; remeasure when index changes")
    if spec["escalation"]["type"] == "greater_of":
        flags.append("greater-of escalator: fixed floor treated as in-substance fixed - reviewer to confirm")
    if spec.get("variable_rent") == "turnover":
        flags.append("turnover rent excluded from liability (variable) - expense as incurred")
    if spec.get("renewal_option") == "present":
        flags.append("renewal option present - lease term is a management judgement (reasonably certain?)")
    if spec.get("termination_option") == "present":
        flags.append("termination option present - lease term is a management judgement")
    liability = sum(a / (1 + r) ** (t / 12) for t, a in flows)
    i = (1 + r) ** (1 / 12) - 1
    bal, rows, tot_int = liability, [], 0.0
    pay_at = {}
    for t, a in flows:
        pay_at[t] = pay_at.get(t, 0) + a
    for m in range(term + 1):
        bal -= pay_at.get(m, 0)
        if m < term:
            interest = bal * i
            bal += interest
            tot_int += interest
            rows.append((m + 1, round(interest, 2)))
    return {"status": "ok", "liability": round(liability, 2), "rou_asset": round(liability, 2),
            "monthly_depreciation": round(liability / term, 2), "total_payments": round(total_paid, 2),
            "total_interest": round(tot_int, 2), "closing_balance": round(bal, 6),
            "schedule_interest": rows, "flags": flags}

def diff_specs(old, new):
    return {k: (old[k], new[k]) for k in old if k in new and old[k] != new[k]}
