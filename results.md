# Deterministic test results

**45/48 deterministic checks passed.** (Tests the checker and calculator only; no LLM involved.)

## A. Calculator vs closed-form expected value
| Case | Result | Detail |
|---|---|---|
| L01 liability | PASS | calc=552121.13 expected=552,121.13 |
| L01 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L02 liability | PASS | calc=772173.49 expected=772,173.49 |
| L02 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L03 liability | PASS | calc=810782.17 expected=810,782.17 |
| L03 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L04 liability | PASS | calc=259918.5 expected=259,918.50 |
| L04 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=-0.0 |
| L05 liability | FAIL | calc=None expected=134,839.44 |
| L06 liability | PASS | calc=225257.51 expected=225,257.51 |
| L06 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L07 liability | PASS | calc=256276.34 expected=256,276.34 |
| L07 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L08 short-term exemption | PASS | status=exempt_short_term expense=25000.0 |
| L09 low-value exemption | PASS | status=exempt_low_value expense=3240.0 |
| L10 liability | PASS | calc=132437.35 expected=132,437.35 |
| L10 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L11 liability | FAIL | calc=260882.82 expected=165,546.69 |
| L11 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |
| L12 silent escalation -> stops | PASS | lease is silent / not extracted: ['escalation'] |
| L13 liability | PASS | calc=386484.79 expected=386,484.79 |
| L13 schedule identity (interest = payments - liability, closes to 0) | PASS | closing=0.0 |

## B. Citation checker on gold extractions (should all pass)
| Case | Result | Detail |
|---|---|---|
| L01 gold extraction passes checker | PASS | all fields verified |
| L02 gold extraction passes checker | PASS | all fields verified |
| L03 gold extraction passes checker | PASS | all fields verified |
| L04 gold extraction passes checker | PASS | all fields verified |
| L05 gold extraction passes checker | PASS | all fields verified |
| L06 gold extraction passes checker | PASS | all fields verified |
| L07 gold extraction passes checker | PASS | all fields verified |
| L08 gold extraction passes checker | PASS | all fields verified |
| L09 gold extraction passes checker | PASS | all fields verified |
| L10 gold extraction passes checker | PASS | all fields verified |
| L11 gold extraction passes checker | PASS | all fields verified |
| L12 gold extraction passes checker | PASS | all fields verified |
| L13 gold extraction passes checker | PASS | all fields verified |

## C. Checker on injected faults (SIMULATED bad model outputs, should be rejected)
| Fault | Result | Detail |
|---|---|---|
| Fabricated quote (clause not in lease) | PASS | quote is not in the source text |
| Paraphrased quote (reworded) | PASS | quote is not in the source text |
| Real quote, wrong number in value | PASS | value 12000 does not appear in its quote |
| Non-null value with no quote | PASS | no quote supplied |
| not_stated but with invented quote | PASS | quote is not in the source text |
| Quote taken from a different lease | PASS | quote is not in the source text |
| Whitespace/line-break difference only (should still PASS) | PASS | ok |

## D. Known gap (documented failure, not hidden)
| Case | Result | Detail |
|---|---|---|
| Real quote, WRONG interpretation (value 'arrears', quote says 'in advance') | NOT CAUGHT | checker is substring-based and cannot judge meaning; this is why a human signs off the spec |
| Unit mix-up (value 10 'months' extracted from 'ten (10) years') | CAUGHT | quote is real and contains the number; unit conversion is not checked; human sign-off covers it |

## E. Pipeline behaviours
| Case | Result | Detail |
|---|---|---|
| L11 amendment diff flags only the term change | FAIL | {} |
| L06 raises a review flag (renewal option) | PASS | renewal option present - lease term is a management judgement (reasonably certain?) |
| L07 raises a review flag (termination option) | PASS | termination option present - lease term is a management judgement |
| L10 raises a review flag (turnover rent) | PASS | turnover rent excluded from liability (variable) - expense as incurred |
| L13 raises a review flag (greater-of) | PASS | greater-of escalator: fixed floor treated as in-substance fixed - reviewer to confirm |
| L04 raises a review flag (CPI) | PASS | CPI-linked: liability measured at current index; remeasure when index changes |
