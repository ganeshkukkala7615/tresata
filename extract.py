
"""Reliable LLM extraction for LeaseLab.
Skips successful outputs and retries temporary API/network failures.
"""
import os
import sys
import json
import time
import re
import socket
import urllib.request
import urllib.error

from leases import LEASES, lease_text

MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

PROMPT = """You extract lease terms from a lease excerpt into JSON. Rules:
- Return ONLY a JSON object, no prose, no markdown fences.
- Every field is {"value": ..., "quote": "<exact text copied from the lease>", "clause": "<clause number>"}.
- The quote must be copied character-for-character from the lease. Never paraphrase.
- If the lease does not state a field, return {"value": "not_stated", "quote": null, "clause": null}. Do NOT guess or assume defaults.
- Do not decide the lease term, the discount rate or whether an option will be exercised. Only report what the text says.
Fields:
 commencement_date: "YYYY-MM-DD"
 base_term_months: integer (convert years to months)
 payment_amount: number, per payment period
 frequency: "monthly" | "quarterly" | "annual"
 timing: "advance" | "arrears"
 escalation: {"type": "none"|"fixed_pct"|"cpi"|"greater_of", "pct": number (if any), "interval_months": integer (if any)}
 free_rent_months: integer
 renewal_option: "present" (if the tenant has a renewal/extension option)
 termination_option: "present" (if the tenant has a break/termination option)
 variable_rent: "turnover" (if any rent depends on sales)
LEASE:
"""


def call(lease):
    body = json.dumps({
        "model": MODEL,
        "temperature": 0,
        "messages": [
            {"role": "user", "content": PROMPT + lease}
        ]
    }).encode("utf-8")

    for attempt in range(4):
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (leaselab-prototype)",
                "HTTP-Referer": "https://localhost",
                "X-Title": "leaselab"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.load(response)
                return result["choices"][0]["message"]["content"]

        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]

            if e.code == 429 or e.code in (500, 502, 503, 504):
                if attempt < 3:
                    wait = 20 * (attempt + 1) if e.code == 429 else 5 * (2 ** attempt)
                    print(f"Temporary HTTP {e.code}. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    continue

            raise RuntimeError(f"HTTP {e.code}: {detail}")

        except (urllib.error.URLError, socket.gaierror,
                ConnectionResetError, TimeoutError, OSError) as e:
            if attempt < 3:
                wait = 5 * (2 ** attempt)
                print(f"Network error: {e}. Retrying in {wait} seconds...")
                time.sleep(wait)
                continue

            raise RuntimeError(f"Network failed after 4 attempts: {e}")

    raise RuntimeError("Maximum retry attempts reached")


def parse(raw):
    raw = re.sub(
        r"^```(?:json)?|```$",
        "",
        raw.strip(),
        flags=re.M
    ).strip()
    return json.loads(raw)


def is_successful(path):
    if not os.path.exists(path):
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return isinstance(data, dict) and "_error" not in data
    except (json.JSONDecodeError, OSError):
        return False


if __name__ == "__main__":
    if not KEY:
        sys.exit("Missing OPENROUTER_API_KEY. Configure it in CMD first.")

    os.makedirs("outputs_llm", exist_ok=True)

    print("Model:", MODEL)
    print("API key: configured (value hidden)")
    print("-" * 50)

    success_count = 0
    failed_count = 0

    for L in LEASES:
        output_path = os.path.join(
            "outputs_llm", f"{L['id']}.json"
        )

        if is_successful(output_path):
            print(f"{L['id']} already successful - SKIPPED")
            success_count += 1
            continue

        print(f"\nProcessing {L['id']}...")

        try:
            raw = call(lease_text(L))
            extracted = parse(raw)

            if not isinstance(extracted, dict):
                raise ValueError("Model response is not a JSON object")

            if "_error" in extracted:
                raise ValueError("Unexpected error in model response")

            temp_path = output_path + ".tmp"

            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)

            os.replace(temp_path, output_path)

            print(f"{L['id']} OK")
            success_count += 1

        except Exception as e:
            print(f"{L['id']} FAILED: {e}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"_error": str(e)}, f, indent=2)

            failed_count += 1

        time.sleep(8)

    print("\n" + "=" * 50)
    print("EXTRACTION SUMMARY")
    print("Successful:", success_count, "/", len(LEASES))
    print("Failed:", failed_count)
    print("=" * 50)
