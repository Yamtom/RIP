import re
from pathlib import Path
import sys
from collections import Counter

def main():
    root = Path(__file__).resolve().parents[1]
    events_dir = root / "events"
    id_pattern = re.compile(r"\bid\s*=\s*(\d+)")
    ids = []
    for txt in events_dir.glob("*.txt"):
        for line in txt.read_text(encoding='utf-8', errors='ignore').splitlines():
            match = id_pattern.search(line)
            if match:
                ids.append(match.group(1))
    duplicates = [id_ for id_, count in Counter(ids).items() if count > 1]
    if duplicates:
        print("Duplicate event IDs found: " + ", ".join(sorted(duplicates)))
        sys.exit(1)
    print("All event IDs are unique.")

if __name__ == "__main__":
    main()
