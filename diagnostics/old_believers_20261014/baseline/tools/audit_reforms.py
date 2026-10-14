#!/usr/bin/env python3
"""audit_reforms.py

This script audits the EU4 mod's government reforms.
It scans all *.txt files under `common/government_reforms`, extracts key information
(name, tier, potential, trigger, modifiers) and compares modifiers against the
vanilla game's `common/event_modifiers` definitions.
It also reports duplicate reform names, unknown tokens and tier imbalance.

Usage:
    python audit_reforms.py
"""

import os
import re
import json
from collections import defaultdict, Counter

# ---------------------------------------------------------------------------
# Configuration – adjust if your folder layout differs
# ---------------------------------------------------------------------------
MOD_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMON_REFORMS_DIR = os.path.join(MOD_ROOT, "common", "government_reforms")
VANILLA_ROOT = r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV"
VANILLA_EVENT_MODIFIERS = os.path.join(VANILLA_ROOT, "common", "event_modifiers")

# Known incorrect tokens (common typos in the mod). Extend as needed.
KNOWN_BAD_TOKENS = {
    "hetmany": "hetmani",
    "boyary": "boyars",
    "knyazi": "knyaz",
    # add more mappings if discovered
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_vanilla_modifiers(path: str) -> set:
    """Return a set of modifier names defined in vanilla `event_modifiers` files."""
    modifiers = set()
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.txt'):
                full = os.path.join(root, f)
                with open(full, encoding='utf-8', errors='ignore') as fh:
                    for line in fh:
                        m = re.match(r"\s*(\w+)\s*=", line)
                        if m:
                            modifiers.add(m.group(1))
    return modifiers

def parse_reform_file(filepath: str) -> dict:
    """Parse a single reform definition file.
    Returns a dict mapping reform_name -> info dict.
    The file may contain multiple reform blocks separated by newlines.
    """
    reforms = {}
    with open(filepath, encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    # Split on top‑level blank lines which usually separate blocks
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        # Find the reform name – appears as a top‑level key followed by "={"
        name_match = re.search(r"^(\w+)\s*=\s*{", block, re.MULTILINE)
        if not name_match:
            continue
        name = name_match.group(1)
        info = {"file": os.path.basename(filepath)}
        # tier
        tier_match = re.search(r"\btier\s*=\s*(\d+)", block)
        if tier_match:
            info["tier"] = int(tier_match.group(1))
        # potential – capture the whole block for later inspection
        pot_match = re.search(r"potential\s*=\s*{([^}]*)}", block, re.DOTALL)
        if pot_match:
            info["potential"] = pot_match.group(1).strip()
        # trigger
        trig_match = re.search(r"trigger\s*=\s*{([^}]*)}", block, re.DOTALL)
        if trig_match:
            info["trigger"] = trig_match.group(1).strip()
        # modifiers – collect all key = value lines inside a "modifier" block
        mods = []
        for mod_match in re.finditer(r"modifier\s*=\s*{([^}]*)}", block, re.DOTALL):
            inner = mod_match.group(1)
            for line in inner.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                kv = re.split(r"\s*=\s*", line, maxsplit=1)
                if len(kv) == 2:
                    mods.append(kv[0])
        if mods:
            info["modifiers"] = mods
        reforms[name] = info
    return reforms

def detect_bad_tokens(text: str) -> list:
    """Return a list of bad tokens found in the provided text.
    Each entry is a dict with keys 'bad' and 'suggested'.
    """
    found = []
    for bad, good in KNOWN_BAD_TOKENS.items():
        if re.search(r"\b" + re.escape(bad) + r"\b", text):
            found.append({"bad": bad, "suggested": good})
    return found

# ---------------------------------------------------------------------------
# Main audit logic
# ---------------------------------------------------------------------------
def main():
    vanilla_mods = load_vanilla_modifiers(VANILLA_EVENT_MODIFIERS)
    all_reforms = {}
    duplicate_names = []
    token_issues = []
    tier_counter = Counter()

    # Walk through mod reform files
    for root, _, files in os.walk(COMMON_REFORMS_DIR):
        for f in files:
            if not f.lower().endswith('.txt'):
                continue
            path = os.path.join(root, f)
            parsed = parse_reform_file(path)
            for name, info in parsed.items():
                # Duplicate detection
                if name in all_reforms:
                    duplicate_names.append(name)
                all_reforms[name] = info
                # Tier stats
                tier = info.get('tier')
                if tier:
                    tier_counter[tier] += 1
                # Token check – run on raw block text
                with open(path, encoding='utf-8', errors='ignore') as fh:
                    raw = fh.read()
                token_issues.extend(detect_bad_tokens(raw))
                # Modifier validation
                mods = info.get('modifiers', [])
                unknown_mods = [m for m in mods if m not in vanilla_mods]
                if unknown_mods:
                    info.setdefault('unknown_modifiers', []).extend(unknown_mods)

    # Tier imbalance – report tiers with unusually low or high counts (heuristic)
    tier_imbalance = {t: c for t, c in tier_counter.items() if c < 5 or c > 12}

    report = {
        "total_reforms": len(all_reforms),
        "duplicate_names": duplicate_names,
        "tier_distribution": dict(tier_counter),
        "tier_imbalance": tier_imbalance,
        "token_issues": token_issues,
        "reforms": all_reforms,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
