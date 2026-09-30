"""Extract 50-year engine counters without treating intermediate saves as final."""
from pathlib import Path
import hashlib
import json
import re
import sys

OUT = Path(__file__).resolve().parent
save = OUT / "userdir/save games/gcpace_final.eu4"
if not save.exists():
    save = OUT / "userdir/save games/autosave.eu4"
if not save.exists():
    raise SystemExit("No engine save available")

raw = save.read_bytes()
lines = raw.decode("latin-1").splitlines()
date = next(line[5:] for line in lines[:10] if line.startswith("date="))
index = lines.index("countries={") + 1
cohorts = {}
tag = None
body = []
while index < len(lines) and lines[index] != "}":
    line = lines[index]
    match = re.match(r"^\t([A-Z0-9]{3})=\{$", line)
    if match:
        tag = match[1]
        body = []
    elif line == "\t}" and tag:
        text = "\n".join(body)
        if "rip_gcpace_cohort=" in text:
            counters = {
                key: float(value)
                for key, value in re.findall(
                    r"^\t\t\trip_gcpace_(\w+)=(-?\d+(?:\.\d+)?)$", text, re.M
                )
            }
            native = {
                key: value
                for key, value in re.findall(
                    r"^\t\t(religion|patriarch_authority|treasury|stability|prestige)=(.*)$",
                    text,
                    re.M,
                )
            }
            modifiers = re.findall(
                r'modifier="(rip_church_gc_[^"]+)"\n\t\t\tdate=([^\n]+)', text
            )
            cohorts[tag] = {
                "native": native,
                "counters": counters,
                "active_modifiers": modifiers,
            }
        tag = None
    elif tag:
        body.append(line)
    index += 1

game_log = (OUT / "userdir/logs/game.log").read_text(
    encoding="utf-8", errors="replace"
)
dates = re.findall(r"EVENT \[([\d.]+)\]", game_log)
errors = (OUT / "userdir/logs/error.log").read_text(
    encoding="utf-8", errors="replace"
)
target_reached = date >= "1495.1.1"
result = {
    "save": save.name,
    "save_sha256": hashlib.sha256(raw).hexdigest(),
    "save_date": date,
    "last_logged_event_date": dates[-1] if dates else None,
    "target_reached": target_reached,
    "cohorts": cohorts,
    "harness_error_lines": sorted(
        set(
            line
            for line in errors.splitlines()
            if "gcpace" in line or "Quoted string longer" in line
        )
    ),
}
(OUT / "observations_50y.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
if not target_reached:
    raise SystemExit("50-year target not reached; this is only an interim extraction")
