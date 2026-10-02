"""EU4 BOM policy; --staged reads the Git index, never the working copy."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BOM = b"\xef\xbb\xbf"
DATA_DIRS = {"common", "customizable_localization", "decisions", "events",
             "history", "map", "missions", "interface", "gfx", "sound"}


def policy(path: str) -> str | None:
    parts = Path(path.replace("\\", "/")).parts
    suffix = Path(path).suffix.lower()
    if len(parts) > 1 and parts[0] not in DATA_DIRS | {"localisation"}:
        return None  # Archived snapshots and other worktrees are not this mod.
    if parts[0] == "localisation" and suffix == ".yml":
        return "required"
    if suffix in {".mod", ".gui", ".gfx"} or (suffix == ".txt" and parts[0] in DATA_DIRS):
        return "forbidden"
    return None


def error(path: str, raw: bytes) -> str | None:
    rule = policy(path)
    if rule is None:
        return None
    if raw.startswith((b"\xff\xfe", b"\xfe\xff", b"\x00\x00\xfe\xff")):
        return "UTF-16/32 is not supported; save as UTF-8"
    if rule == "forbidden" and raw.startswith(BOM):
        return "UTF-8 BOM is forbidden in engine data/descriptors"
    if rule == "required" and not raw.startswith(BOM):
        return "localisation requires a UTF-8 BOM"
    if rule == "required" and raw.startswith(BOM + BOM):
        return "duplicate UTF-8 BOM"
    return None


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    if args.staged:
        paths = [p.decode("utf-8") for p in git_bytes("diff", "--cached", "--name-only",
                 "--diff-filter=ACMR", "-z").split(b"\0") if p]
        rows = ((p, git_bytes("show", ":" + p)) for p in paths if policy(p))
    else:
        candidates = list(ROOT.glob("*.mod"))
        for directory in sorted(DATA_DIRS | {"localisation"}):
            candidates.extend((ROOT / directory).rglob("*"))
        rows = ((p.relative_to(ROOT).as_posix(), p.read_bytes())
                for p in sorted(candidates)
                if p.is_file() and policy(p.relative_to(ROOT).as_posix()))
    checked = 0
    failures = []
    for path, raw in rows:
        checked += 1
        issue = error(path, raw)
        if issue:
            failures.append(f"{path}: {issue}")
    for failure in failures:
        print(f"ERROR {failure}")
    print(f"ENCODING {'FAIL' if failures else 'PASS'}: {checked} files; {len(failures)} violations")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
