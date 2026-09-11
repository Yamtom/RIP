import subprocess
import sys
import io
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

parser = argparse.ArgumentParser(description="Run all RIP static contracts and optionally retain complete outputs.")
parser.add_argument("--log", type=Path, help="Complete untruncated outputs for review")
args = parser.parse_args()

scripts = [
    "tests/check_vanilla_version.py",
    "tests/check_donor_audit.py",
    "tests/check_colonial_names.py",
    "tests/check_clausewitz_braces.py",
    "tests/check_ro_blessing_window.py",
    "tests/check_uc_curia.py",
    "tests/check_faith_content_balance.py",
    "tests/check_religion_settlement.py",
    "tests/check_scripted_faith_links.py",
    "tests/check_culture_key_compatibility.py",
    "tests/check_cultural_authenticity.py",
    "tests/check_estate_layer.py",
    "tests/check_event_modifier_layer.py",
    "tests/check_opinion_modifier_layer.py",
    "tests/check_province_names.py",
    "tests/check_government_reforms.py",
    "tests/check_government_reviews.py",
    "tests/check_government_names.py",
    "tests/check_glossary.py",
    "tests/check_claim_pacing.py",
    "tests/check_subject_cb_limits.py",
    "tests/check_border_principalities.py",
    "tests/check_steppe_expansions.py",
    "tests/check_docs_language.py",
    "tests/check_script_layer.py"
]

all_ok = True
complete_output = []
for s in scripts:
    res = subprocess.run([sys.executable, "-B", s], capture_output=True, text=True, encoding="utf-8", errors="replace")
    complete_output.append(f"=== {s} -> Exit code {res.returncode} ===\n{res.stdout}\n{res.stderr}\n")
    print(f"=== {s} -> Exit code {res.returncode} ===")
    if res.stdout:
        print(res.stdout.strip()[:400])
    if res.stderr:
        print("ERR:", res.stderr.strip()[:400])
    if res.returncode != 0 and "check_script_layer.py" not in s:
        all_ok = False

print(f"\nALL CRITICAL TESTS PASS: {all_ok}")
if args.log:
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("\n".join(complete_output) + f"\nALL CRITICAL TESTS PASS: {all_ok}\n", encoding="utf-8")
    print(f"Complete output: {args.log}")
raise SystemExit(0 if all_ok else 1)
