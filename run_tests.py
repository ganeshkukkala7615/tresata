"""Deterministic tests. These test the CHECKER and the CALCULATOR only - not any LLM.
Expected values come from closed-form formulas (different code path from calc.py)."""
import copy
from leases import LEASES, lease_text, AMENDMENT_GOLD_L11, F
from checker import check_extraction, check_field, all_ok
from calc import to_spec, compute, diff_specs

def eff(r, months): return (1 + r) ** (months / 12) - 1
def annuity(P, j, N, advance):           # level payments, N periods, period rate j
    pv = P * (1 - (1 + j) ** -N) / j
    return pv * (1 + j) if advance else pv

def expected(lid):
    L = {x["id"]: x for x in LEASES}[lid]; r = L["human"]["rate"]
    if lid == "L02": return 772173.49                      # textbook anchor
    if lid == "L03": return 810782.17                      # textbook anchor x 1.05
    if lid == "L04": return annuity(8000, eff(r, 1), 36, False)
    if lid == "L05":
        v = 1 / (1 + eff(r, 1)); return 5000 * v ** 6 * (1 - v ** 30) / (1 - v)
    if lid == "L06": return annuity(50000, r, 5, True)
    if lid == "L07": return annuity(6000, eff(r, 1), 48, False)
    if lid == "L10": return annuity(4000, eff(r, 1), 36, True)
    if lid in ("L01", "L13"):
        g = 0.03; P = 10000 if lid == "L01" else 7000; i = eff(r, 1)
        block = annuity(P, i, 12, True)
        return sum(block * (1 + g) ** y / (1 + r) ** y for y in range(5))
    if lid == "L11": return annuity(5000, eff(r, 1), 36, True)
    return None

lines, passed, total = [], 0, 0
def rec(name, ok, detail=""):
    global passed, total
    total += 1; passed += bool(ok)
    lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")

lines += ["## A. Calculator vs closed-form expected value", "| Case | Result | Detail |", "|---|---|---|"]
for L in LEASES:
    spec = to_spec(L["gold"]); out = compute(spec, L["human"]); lid = L["id"]
    if lid == "L08":
        rec(f"{lid} short-term exemption", out["status"] == "exempt_short_term" and out["expense"] == 25000, f"status={out['status']} expense={out.get('expense')}")
    elif lid == "L09":
        rec(f"{lid} low-value exemption", out["status"] == "exempt_low_value" and out["expense"] == 3240, f"status={out['status']} expense={out.get('expense')}")
    elif lid == "L12":
        rec(f"{lid} silent escalation -> stops", out["status"] == "needs_human", out.get("reason", ""))
    else:
        e = expected(lid); tol = 0.5 if lid in ("L02", "L03") else 0.01
        ok = out["status"] == "ok" and abs(out["liability"] - e) <= tol
        rec(f"{lid} liability", ok, f"calc={out.get('liability')} expected={e:,.2f}")
        if out["status"] == "ok":
            ident = abs(out["total_interest"] - (out["total_payments"] - out["liability"])) < 0.05 and abs(out["closing_balance"]) < 0.01
            rec(f"{lid} schedule identity (interest = payments - liability, closes to 0)", ident, f"closing={out['closing_balance']}")

lines += ["", "## B. Citation checker on gold extractions (should all pass)", "| Case | Result | Detail |", "|---|---|---|"]
for L in LEASES:
    res = check_extraction(L["gold"], lease_text(L)); bad = {k: m for k, (ok, m) in res.items() if not ok}
    rec(f"{L['id']} gold extraction passes checker", all_ok(res), str(bad) if bad else "all fields verified")

lines += ["", "## C. Checker on injected faults (SIMULATED bad model outputs, should be rejected)", "| Fault | Result | Detail |", "|---|---|---|"]
src = lease_text(LEASES[0]); g = LEASES[0]["gold"]
faults = [
 ("Fabricated quote (clause not in lease)", "payment_amount", F(10000, "Rent of USD 10,000 shall be paid monthly", "3.1"), False),
 ("Paraphrased quote (reworded)", "payment_amount", F(10000, "ten thousand dollars every month", "3.1"), False),
 ("Real quote, wrong number in value", "payment_amount", F(12000, "USD 10,000 per month", "3.1"), False),
 ("Non-null value with no quote", "free_rent_months", F(3, None, None), False),
 ("not_stated but with invented quote", "free_rent_months", F("not_stated", "three months free", "3.3"), False),
 ("Quote taken from a different lease", "payment_amount", F(8000, "Monthly rent is USD 8,000", "3.1"), False),
 ("Whitespace/line-break difference only (should still PASS)", "timing", F("advance", "payable monthly   in\nadvance", "3.1"), True),
]
for name, fld, field, should_pass in faults:
    ok, msg = check_field(fld, field, src); rec(name, ok == should_pass, msg)

lines += ["", "## D. Known gap (documented failure, not hidden)", "| Case | Result | Detail |", "|---|---|---|"]
ok, msg = check_field("timing", F("arrears", "payable monthly in advance", "3.1"), src)
lines.append(f"| Real quote, WRONG interpretation (value 'arrears', quote says 'in advance') | {'CAUGHT' if not ok else 'NOT CAUGHT'} | checker is substring-based and cannot judge meaning; this is why a human signs off the spec |")
src2 = lease_text([x for x in LEASES if x["id"] == "L02"][0])
ok, msg = check_field("base_term_months", F(10, "ten (10) years", "2.1"), src2)
lines.append(f"| Unit mix-up (value 10 'months' extracted from 'ten (10) years') | {'CAUGHT' if not ok else 'NOT CAUGHT'} | quote is real and contains the number; unit conversion is not checked; human sign-off covers it |")

lines += ["", "## E. Pipeline behaviours", "| Case | Result | Detail |", "|---|---|---|"]
l11 = [x for x in LEASES if x["id"] == "L11"][0]
old = to_spec(l11["gold"]); new = copy.deepcopy(l11["gold"]); new.update(AMENDMENT_GOLD_L11)
d = diff_specs(old, to_spec(new)); rec("L11 amendment diff flags only the term change", d == {"base_term_months": (36, 60)}, str(d))
for lid, key in (("L06", "renewal option"), ("L07", "termination option"), ("L10", "turnover rent"), ("L13", "greater-of"), ("L04", "CPI")):
    L = [x for x in LEASES if x["id"] == lid][0]; out = compute(to_spec(L["gold"]), L["human"])
    rec(f"{lid} raises a review flag ({key})", any(key.split()[0].lower() in f.lower() for f in out["flags"]), "; ".join(out["flags"]))

summary = f"**{passed}/{total} deterministic checks passed.** (Tests the checker and calculator only; no LLM involved.)\n"
open("results.md", "w").write("# Deterministic test results\n\n" + summary + "\n" + "\n".join(lines) + "\n")
print(summary); print("\n".join(lines))
