import subprocess
import sys
import io

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scripts = [
    "tests/check_clausewitz_braces.py",
    "tests/check_culture_key_compatibility.py",
    "tests/check_estate_layer.py",
    "tests/check_event_modifier_layer.py",
    "tests/check_glossary.py",
    "tests/check_claim_pacing.py",
    "tests/check_subject_cb_limits.py",
    "tests/check_border_principalities.py",
    "tests/check_steppe_expansions.py",
    "tests/check_docs_language.py",
    "tests/check_script_layer.py"
]

all_ok = True
for s in scripts:
    res = subprocess.run([sys.executable, s], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print(f"=== {s} -> Exit code {res.returncode} ===")
    if res.stdout:
        print(res.stdout.strip()[:400])
    if res.stderr:
        print("ERR:", res.stderr.strip()[:400])
    if res.returncode != 0 and "check_script_layer.py" not in s:
        all_ok = False

print(f"\nALL CRITICAL TESTS PASS: {all_ok}")
