"""13 SYNTHETIC lease excerpts (all made up for this prototype).
Each has: clauses (ref, text), gold extraction (value, quote), and human inputs
(lease term decision, discount rate) that the accountant -- not the model -- supplies.
"""

def L(id, title, clauses, gold, human, note=""):
    return dict(id=id, title=title, clauses=clauses, gold=gold, human=human, note=note)


def F(value, quote=None, clause=None):
    return {"value": value, "quote": quote, "clause": clause}


NS = F("not_stated")

LEASES = [
    L("L01", "Office - fixed 3% annual escalation, monthly in advance",
      [
          ("1.1", "Commencement Date: 1 January 2025."),
          ("2.1", "The Term is sixty (60) months from the Commencement Date."),
          ("3.1", "Tenant shall pay Base Rent of USD 10,000 per month, payable monthly in advance on the first day of each month."),
          ("3.2", "Base Rent shall increase by three percent (3%) on each anniversary of the Commencement Date.")
      ],
      dict(
          commencement_date=F("2025-01-01", "Commencement Date: 1 January 2025", "1.1"),
          base_term_months=F(60, "sixty (60) months", "2.1"),
          payment_amount=F(10000, "USD 10,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "fixed_pct", "pct": 3, "interval_months": 12}, "increase by three percent (3%) on each anniversary", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=60, rate=0.06)
    ),

    L("L02", "Warehouse - flat annual rent in arrears (textbook anchor)",
      [
          ("1.1", "Commencement Date: 1 April 2025."),
          ("2.1", "The Term is ten (10) years."),
          ("3.1", "Tenant shall pay annual rent of USD 100,000, payable annually in arrears on each anniversary of the Commencement Date."),
          ("3.2", "The annual rent is fixed and shall not be adjusted during the Term.")
      ],
      dict(
          commencement_date=F("2025-04-01", "Commencement Date: 1 April 2025", "1.1"),
          base_term_months=F(120, "ten (10) years", "2.1"),
          payment_amount=F(100000, "annual rent of USD 100,000", "3.1"),
          frequency=F("annual", "payable annually", "3.1"),
          timing=F("arrears", "in arrears", "3.1"),
          escalation=F({"type": "none"}, "fixed and shall not be adjusted", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=120, rate=0.05)
    ),

    L("L03", "Warehouse - same as L02 but annual rent in advance",
      [
          ("1.1", "Commencement Date: 1 April 2025."),
          ("2.1", "The Term is ten (10) years."),
          ("3.1", "Tenant shall pay annual rent of USD 100,000, payable annually in advance on the Commencement Date and each anniversary."),
          ("3.2", "The annual rent is fixed and shall not be adjusted during the Term.")
      ],
      dict(
          commencement_date=F("2025-04-01", "Commencement Date: 1 April 2025", "1.1"),
          base_term_months=F(120, "ten (10) years", "2.1"),
          payment_amount=F(100000, "annual rent of USD 100,000", "3.1"),
          frequency=F("annual", "payable annually", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "fixed and shall not be adjusted", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=120, rate=0.05)
    ),

    L("L04", "Retail unit - CPI-linked rent (index at commencement only)",
      [
          ("1.1", "Commencement Date: 1 July 2025."),
          ("2.1", "The Term is thirty-six (36) months."),
          ("3.1", "Monthly rent is USD 8,000, payable monthly in arrears."),
          ("3.2", "On each anniversary, the rent shall be adjusted in line with the Consumer Price Index published by the national statistics office.")
      ],
      dict(
          commencement_date=F("2025-07-01", "Commencement Date: 1 July 2025", "1.1"),
          base_term_months=F(36, "thirty-six (36) months", "2.1"),
          payment_amount=F(8000, "Monthly rent is USD 8,000", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("arrears", "in arrears", "3.1"),
          escalation=F({"type": "cpi"}, "adjusted in line with the Consumer Price Index", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=36, rate=0.07)
    ),

    L("L05", "Office - six months rent-free at start",
      [
          ("1.1", "Commencement Date: 1 February 2025."),
          ("2.1", "The Term is thirty-six (36) months."),
          ("3.1", "Rent is USD 5,000 per month, payable monthly in advance."),
          ("3.2", "No rent is payable for the first six (6) months of the Term (the Rent-Free Period).")
      ],
      dict(
          commencement_date=F("2025-02-01", "Commencement Date: 1 February 2025", "1.1"),
          base_term_months=F(36, "thirty-six (36) months", "2.1"),
          payment_amount=F(5000, "USD 5,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=NS,
          free_rent_months=F(6, "first six (6) months of the Term", "3.2"),
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=36, rate=0.065)
    ),

    L("L06", "Clinic - five years plus tenant renewal option at market rent",
      [
          ("1.1", "Commencement Date: 1 September 2025."),
          ("2.1", "The initial Term is five (5) years."),
          ("2.2", "Tenant may renew for one further term of five (5) years on twelve (12) months' written notice, at the then open-market rent."),
          ("3.1", "Annual rent is USD 50,000, payable annually in advance."),
          ("3.2", "Rent is fixed during the initial Term.")
      ],
      dict(
          commencement_date=F("2025-09-01", "Commencement Date: 1 September 2025", "1.1"),
          base_term_months=F(60, "initial Term is five (5) years", "2.1"),
          payment_amount=F(50000, "Annual rent is USD 50,000", "3.1"),
          frequency=F("annual", "payable annually", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "Rent is fixed during the initial Term", "3.2"),
          free_rent_months=NS,
          renewal_option=F("present", "Tenant may renew for one further term of five (5) years", "2.2"),
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=60, rate=0.055),
      "Human judgement: renewal at market rent, not reasonably certain -> excluded from term."
    ),

    L("L07", "Depot - tenant break option after 24 months with penalty",
      [
          ("1.1", "Commencement Date: 1 March 2025."),
          ("2.1", "The Term is forty-eight (48) months."),
          ("2.2", "Tenant may terminate this Lease after the twenty-fourth (24) month by giving three (3) months' notice and paying a termination fee equal to six (6) months' rent."),
          ("3.1", "Rent is USD 6,000 per month, payable monthly in arrears."),
          ("3.2", "Rent is fixed throughout the Term.")
      ],
      dict(
          commencement_date=F("2025-03-01", "Commencement Date: 1 March 2025", "1.1"),
          base_term_months=F(48, "forty-eight (48) months", "2.1"),
          payment_amount=F(6000, "USD 6,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("arrears", "in arrears", "3.1"),
          escalation=F({"type": "none"}, "Rent is fixed throughout the Term", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=F("present", "Tenant may terminate this Lease after the twenty-fourth (24) month", "2.2"),
          variable_rent=NS
      ),
      dict(term_months=48, rate=0.06),
      "Human judgement: penalty is meaningful -> not reasonably certain to terminate."
    ),

    L("L08", "Pop-up shop - 10 month lease (short-term exemption)",
      [
          ("1.1", "Commencement Date: 1 October 2025."),
          ("2.1", "The Term is ten (10) months and there is no option to extend."),
          ("3.1", "Rent is USD 2,500 per month, payable monthly in advance."),
          ("3.2", "Rent is fixed throughout the Term.")
      ],
      dict(
          commencement_date=F("2025-10-01", "Commencement Date: 1 October 2025", "1.1"),
          base_term_months=F(10, "ten (10) months", "2.1"),
          payment_amount=F(2500, "USD 2,500 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "Rent is fixed throughout the Term", "3.2"),
          free_rent_months=NS,
          renewal_option=F("not_stated", "there is no option to extend.", "2.1"),
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=10, rate=0.06)
    ),

    L("L09", "Laptop fleet lease - low-value asset exemption",
      [
          ("1.1", "Commencement Date: 1 January 2025."),
          ("2.1", "The Term is thirty-six (36) months."),
          ("3.1", "Rental is USD 90 per month per device, payable monthly in advance."),
          ("3.2", "Rental is fixed throughout the Term.")
      ],
      dict(
          commencement_date=F("2025-01-01", "Commencement Date: 1 January 2025", "1.1"),
          base_term_months=F(36, "thirty-six (36) months", "2.1"),
          payment_amount=F(90, "USD 90 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "Rental is fixed throughout the Term", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=36, rate=0.06, asset_value_new=1800),
      "Accountant enters new-asset value (USD 1,800 per device) - not in the contract."
    ),

    L("L10", "Mall store - base rent plus turnover rent",
      [
          ("1.1", "Commencement Date: 1 June 2025."),
          ("2.1", "The Term is thirty-six (36) months."),
          ("3.1", "Base Rent is USD 4,000 per month, payable monthly in advance."),
          ("3.2", "In addition, Tenant shall pay five percent (5%) of gross sales exceeding USD 600,000 in each lease year."),
          ("3.3", "Base Rent is fixed throughout the Term.")
      ],
      dict(
          commencement_date=F("2025-06-01", "Commencement Date: 1 June 2025", "1.1"),
          base_term_months=F(36, "thirty-six (36) months", "2.1"),
          payment_amount=F(4000, "Base Rent is USD 4,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "Base Rent is fixed throughout the Term", "3.3"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=F("turnover", "five percent (5%) of gross sales exceeding USD 600,000", "3.2")
      ),
      dict(term_months=36, rate=0.06)
    ),

    L("L11", "Office - original lease (amendment extends term, see amendment_gold)",
      [
          ("1.1", "Commencement Date: 1 January 2024."),
          ("2.1", "The Term is thirty-six (36) months."),
          ("3.1", "Rent is USD 5,000 per month, payable monthly in advance."),
          ("3.2", "Rent is fixed throughout the Term."),
          ("A1.1", "AMENDMENT No. 1: Clause 2.1 is deleted and replaced with: The Term is sixty (60) months.")
      ],
      dict(
          commencement_date=F("2024-01-01", "Commencement Date: 1 January 2024", "1.1"),
          base_term_months=F(60, "The Term is sixty (60) months", "A1.1"),
          payment_amount=F(5000, "USD 5,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "none"}, "Rent is fixed throughout the Term", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=60, rate=0.06),
      "Amendment No. 1 replaces the original 36-month term with an effective 60-month term."
    ),

    L("L12", "Kiosk - lease is silent on escalation",
      [
          ("1.1", "Commencement Date: 1 August 2025."),
          ("2.1", "The Term is twenty-four (24) months."),
          ("3.1", "Rent is USD 3,000 per month, payable monthly in arrears.")
      ],
      dict(
          commencement_date=F("2025-08-01", "Commencement Date: 1 August 2025", "1.1"),
          base_term_months=F(24, "twenty-four (24) months", "2.1"),
          payment_amount=F(3000, "USD 3,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("arrears", "in arrears", "3.1"),
          escalation=NS,
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=24, rate=0.06),
      "Silence must NOT be silently read as 'no escalation' - system must stop and ask."
    ),

    L("L13", "Showroom - 'greater of 3% or CPI' escalator",
      [
          ("1.1", "Commencement Date: 1 May 2025."),
          ("2.1", "The Term is sixty (60) months."),
          ("3.1", "Rent is USD 7,000 per month, payable monthly in advance."),
          ("3.2", "On each anniversary the rent shall increase by the greater of three percent (3%) and the percentage increase in the Consumer Price Index.")
      ],
      dict(
          commencement_date=F("2025-05-01", "Commencement Date: 1 May 2025", "1.1"),
          base_term_months=F(60, "sixty (60) months", "2.1"),
          payment_amount=F(7000, "USD 7,000 per month", "3.1"),
          frequency=F("monthly", "payable monthly", "3.1"),
          timing=F("advance", "in advance", "3.1"),
          escalation=F({"type": "greater_of", "pct": 3, "interval_months": 12}, "increase by the greater of three percent (3%) and the percentage increase", "3.2"),
          free_rent_months=NS,
          renewal_option=NS,
          termination_option=NS,
          variable_rent=NS
      ),
      dict(term_months=60, rate=0.06),
      "Judgement flag: the 3% floor is treated as in-substance fixed; CPI part is not forecast."
    ),
]

AMENDMENT_GOLD_L11 = {
    "base_term_months": F(60, "The Term is sixty (60) months", "A1.1")
}


def lease_text(lease):
    return "\n".join(f"{ref}. {t}" for ref, t in lease["clauses"])