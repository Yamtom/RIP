import re
import sys
from collections import Counter
from pathlib import Path


LOCALISATION_KEY_PATTERN = re.compile(r"^ [A-Za-z0-9_.-]+:(?:\d+)? \".*\"$")


def check_event_ids(root: Path) -> list[str]:
    events_dir = root / "events"
    id_pattern = re.compile(r"\bid\s*=\s*(\d+)")
    ids: list[str] = []
    for txt in events_dir.glob("*.txt"):
        content = txt.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            match = id_pattern.search(line)
            if match:
                ids.append(match.group(1))
    duplicates = [id_ for id_, count in Counter(ids).items() if count > 1]
    if duplicates:
        return [
            "Duplicate event IDs found: " + ", ".join(sorted(duplicates))
        ]
    return []


def iter_localisation_files(root: Path):
    loc_dir = root / "localisation"
    if not loc_dir.exists():
        return []
    return sorted(loc_dir.rglob("*.yml"))


def detect_language_from_filename(path: Path) -> str | None:
    match = re.search(r"_l_([a-z]+)\\.yml$", path.name, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower()


def check_localisation_format(root: Path) -> list[str]:
    problems: list[str] = []
    for path in iter_localisation_files(root):
        language = detect_language_from_filename(path)
        if language is None:
            problems.append(f"{path}: filename must end with _l_<language>.yml")
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
        except UnicodeDecodeError:
            problems.append(f"{path}: file must be encoded as UTF-8 or UTF-8-BOM")
            continue
        header_found = False
        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.lstrip("\ufeff")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            expected_header = f"l_{language}:"
            if not header_found:
                if stripped != expected_header:
                    problems.append(
                        f"{path}:{idx}: first non-empty line must be '{expected_header}'"
                    )
                header_found = True
                continue
            if not line.startswith(" "):
                problems.append(
                    f"{path}:{idx}: localisation entries must start with exactly one leading space"
                )
                continue
            entry = line[1:]
            if entry.startswith("#"):
                continue
            if not LOCALISATION_KEY_PATTERN.match(line):
                problems.append(
                    f"{path}:{idx}: invalid localisation entry format"
                )
        if not header_found:
            problems.append(f"{path}: missing language header 'l_{language}:'")
    return problems


def main():
    root = Path(__file__).resolve().parents[1]
    errors = []
    errors.extend(check_event_ids(root))
    errors.extend(check_localisation_format(root))
    if errors:
        print("Localisation validation failed:")
        for issue in errors:
            print(f" - {issue}")
        sys.exit(1)
    print("All event IDs are unique.")
    print("Localisation files follow EU4 formatting guidelines.")


if __name__ == "__main__":
    main()
