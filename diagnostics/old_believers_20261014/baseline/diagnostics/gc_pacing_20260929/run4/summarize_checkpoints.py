"""Summarize actual EU4 save snapshots from the synthetic pacing campaign."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
CHECKPOINTS = ROOT / "checkpoints"


def read_save(path: Path) -> tuple[str, dict[str, dict[str, object]]]:
    lines = path.read_bytes().decode("latin-1").splitlines()
    date = next(line[5:] for line in lines[:10] if line.startswith("date="))
    index = lines.index("countries={") + 1
    cohorts: dict[str, dict[str, object]] = {}
    tag = None
    body: list[str] = []
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
                cohorts[tag] = {"native": native, "counters": counters}
            tag = None
        elif tag:
            body.append(line)
        index += 1
    return date, cohorts


files = sorted(CHECKPOINTS.glob("checkpoint_*.eu4"))
if not files:
    raise SystemExit("No five-year checkpoints have been captured yet")

for path in files:
    date, cohorts = read_save(path)
    print(f"\n{date} ({path.name})")
    print("tag  Faith          PA      n    icon-ready  synod-ready  synod-active  icon-active  Orthodox-prov  GC-prov  Orthodox-countries")
    for tag, data in cohorts.items():
        native = data["native"]
        counters = data["counters"]
        icon_active = sum(counters.get(key, 0) for key in ("liturgy", "learning", "charity"))
        pa = counters.get("hc", native.get("patriarch_authority", "n/a"))
        pa_display = f"{float(pa):.3f}" if pa != "n/a" else "n/a"
        print(
            f"{tag:3}  {native.get('religion', 'unknown'):13}  "
            f"{pa_display:>5}  {int(counters.get('n', 0)):4}  "
            f"{int(counters.get('icon_ready', 0)):11}  "
            f"{int(counters.get('synod_ready', 0)):11}  "
            f"{int(counters.get('synod_locked', 0)):12}  {int(icon_active):12}  "
            f"{int(counters.get('orthodox_provinces', 0)):13}  "
            f"{int(counters.get('gc_provinces', 0)):7}  "
            f"{int(counters.get('orthodox_countries', 0)):19}"
        )
