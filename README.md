# LeaseLab — AI-Assisted Lease Extraction and Lease Liability Prototype

**Take-home assignment project | Lessee accounting under IFRS 16 / Ind AS 116**

All 13 lease examples in this project are synthetic. No real company, client, or personal financial data is used.

## 1. Problem

Lease agreements contain important accounting information in unstructured contractual language. Finance teams must identify lease commencement dates, terms, payment amounts, payment timing, rent-free periods, escalation clauses, and renewal options before calculating lease liabilities.

Manual extraction can be time-consuming and inconsistent. An unsupported or incorrect interpretation can also lead to an incorrect accounting calculation.

LeaseLab explores how an LLM can assist with extracting lease information while deterministic checks, calculations, and human review retain control over accounting decisions.

## 2. Proposed solution

The prototype follows a human-in-the-loop workflow:

1. **Input:** A synthetic lease excerpt.
2. **AI extraction:** The LLM extracts structured fields and provides a supporting verbatim quote and clause reference.
3. **Citation checking:** A deterministic checker verifies whether the quote appears in the source and whether selected numeric values are supported by the quote.
4. **Human review:** A reviewer supplies or confirms accounting judgements, including the lease term and discount rate.
5. **Calculation:** A deterministic Python calculator computes lease cash flows and present value, generates an interest schedule, and applies the prototype's exemption logic.
6. **Evaluation:** Model extractions are compared with predefined gold answers.

The LLM does not independently approve accounting treatment or determine the final discount rate.

## 3. Architecture

```text
Synthetic Lease Agreement
          |
          v
    LLM Extraction
          |
          v
Structured Fields + Quotes
          |
          v
Deterministic Citation Checker
          |
          v
     Human Review
          |
          v
Human-Approved Inputs
          |
          v
Deterministic Lease Calculator
          |
          v
Liability / Exemption / Review Output
          |
          v
     Evaluation Report
```

### Architecture decisions

- **LLM:** Used for interpreting unstructured contractual language and extracting candidate fields.
- **Deterministic checker:** Used for traceability and basic numeric consistency.
- **Human reviewer:** Retains responsibility for accounting judgements and ambiguous clauses.
- **Python calculator:** Used for financial arithmetic because calculations should be reproducible and auditable.
- **Retrieval:** Not required for this small synthetic prototype. A production system would need controlled, versioned access to applicable accounting guidance.
- **Agents:** Not used because the workflow is limited and sequential. Multiple autonomous agents would add complexity without a demonstrated benefit.

## 4. Prototype evaluation

The prototype was tested on 13 synthetic lease examples, with 10 gold fields per lease.

| Evaluation metric | Result |
|---|---:|
| Synthetic leases tested | 13 |
| Fields evaluated | 130 |
| Correct fields | 130 |
| Rejected by citation checker | 0 |
| Wrong but accepted | 0 |
| Field-level result | 130/130 |

**Observed result:** All 130 extracted fields matched the predefined gold answers in this evaluation run.

This result is specific to the 13 synthetic examples and the tested model run. It does not establish general accuracy on real contracts.

### Lease-level calculation outcomes

| Lease | Calculator outcome |
|---|---|
| L01 | OK — 552,121.13 |
| L02 | OK — 772,173.49 |
| L03 | OK — 810,782.17 |
| L04 | OK — 259,918.50 |
| L05 | Needs human review |
| L06 | OK — 225,257.51 |
| L07 | OK — 256,276.34 |
| L08 | Short-term exemption — 25,000.00 |
| L09 | Low-value exemption — 3,240.00 |
| L10 | OK — 132,437.35 |
| L11 | OK — 260,882.82 |
| L12 | Needs human review |
| L13 | OK — 386,484.79 |

The amounts are prototype outputs, not independently validated accounting conclusions.

### Deterministic testing

The deterministic test suite reported **49/49 checks passed**. These tests cover calculator behaviour, citation validation, fault cases, and pipeline behaviour.

They are separate from the 130-field LLM evaluation and should not be interpreted as an additional measure of model accuracy.

## 5. Limitations and risks

### Extraction and citation risk
The citation checker confirms that a supporting quote exists in the source and checks selected numeric values. It is not a complete semantic verifier. A quote can be genuine while its interpretation is wrong.

### Accounting judgement risk
Lease classification, lease term, renewal options, discount rates, and other accounting decisions can require professional judgement. Human review and sign-off are necessary.

### Outdated guidance
Accounting standards and interpretations may change. A production system would need version-controlled, authoritative accounting guidance and a process for updating it.

### Confidentiality
Real contracts may contain confidential financial and commercial information. Production deployment would require access controls, appropriate data retention policies, secure model integration, and organisational approval.

### Calculation limitations
The calculator is deliberately simplified. It does not fully model modifications and remeasurements, initial direct costs, incentives, prepayments, stub periods, day-count conventions, foreign exchange, or every lease-specific accounting judgement.

CPI and greater-of escalation clauses are simplified and may require human review.

### Exemption assumptions
The low-value threshold and exemption treatment are prototype assumptions. They must be checked against the applicable accounting standard and accounting policy before production use.

## 6. Why AI instead of a fully manual workflow?

An LLM can help convert contractual language into structured candidate data and attach supporting quotes. This can reduce repetitive manual extraction work.

However, AI should not replace deterministic financial calculations or professional accounting judgement. LeaseLab therefore uses AI for extraction and conventional software for validation, review gates, and calculations.

## 7. Running the prototype

Requirements:
- Windows 10/11
- Python 3.10 or newer
- Internet access for LLM extraction
- OpenRouter API key for extraction

Run deterministic tests:

```bat
python run_tests.py
```

Configure the API key in the current CMD session:

```bat
set OPENROUTER_API_KEY=YOUR_API_KEY
set OPENROUTER_MODEL=openrouter/free
```

Run extraction and evaluation:

```bat
python extract.py
python run_eval.py
```

The deterministic tests do not require an API key. Never commit API keys or generated secrets to a public repository.

## 8. Project files

| File | Purpose |
|---|---|
| `leases.py` | Synthetic lease examples, gold answers, and human inputs |
| `extract.py` | LLM extraction through OpenRouter |
| `checker.py` | Deterministic quote and numeric consistency checks |
| `calc.py` | Lease liability calculator |
| `run_tests.py` | Deterministic test suite |
| `run_eval.py` | Gold-answer evaluation |
| `outputs_llm/` | Saved LLM extraction outputs |
| `eval_report.md` | Field-level evaluation report |
| `results.md` | Deterministic test results |

## 9. Future improvements

- Test on a larger and independently prepared set of synthetic contracts.
- Add semantic validation for payment timing, units, and clause relationships.
- Introduce version-controlled accounting guidance retrieval.
- Improve amendment and modification handling.
- Add reviewer approval, audit logs, and exception tracking.
- Validate calculations independently against authoritative accounting examples.

## 10. Model evaluation record

- Model identifier: `openrouter/free`
- Synthetic leases evaluated: 13
- Fields evaluated: 130
- Correct: 130
- Rejected by checker: 0
- Wrong but accepted: 0
- Deterministic tests: 49/49 passed

**Conclusion:** LeaseLab demonstrates a controlled AI-assisted workflow in which an LLM extracts contractual information, deterministic checks provide basic evidence validation, human reviewers retain accounting responsibility, and a Python calculator performs the financial arithmetic.