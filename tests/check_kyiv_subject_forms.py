"""Registry of the places that create udil-type subjects, against docs/KYIV_SUBJECT_FORMS.uk.md.

`princedom` (hereditary) and `senior_udil` (rotational) are created in a handful
of places that look alike and behave differently. This gate fixes the list: a new
`subject_type = princedom|senior_udil` anywhere in the scripts, or a path that
stops existing, fails until the document and the list below are updated together.

Static only: it reads text, it does not prove any of those paths fires in the game.
"""
import re
from pathlib import Path

from clausewitz_testlib import ROOT, read

# file -> subject types it creates with `subject_type = ...`
CREATION_PATHS = {
    "common/new_diplomatic_actions/RIP_KIE_diplomatic_actions.txt": {"princedom", "senior_udil"},
    "common/new_diplomatic_actions/RIP_PLC_diplomatic_actions.txt": {"princedom"},
    "common/on_actions/RIP_KIE_on_actions.txt": {"princedom"},
    "decisions/KyivTriggers.txt": {"senior_udil"},
    "events/RIP_KIE_KyivShogunate.txt": {"senior_udil"},
    "events/RIP_KIE_kyiv_independence.txt": {"princedom"},
}
# Files that add the rota-counted modifier. The rota counts it, not the subject type.
HELD_AS_AN_UDIL_ADDED_IN = {
    "common/new_diplomatic_actions/RIP_KIE_diplomatic_actions.txt",
    "common/on_actions/RIP_KIE_on_actions.txt",
}
SCRIPT_DIRS = ("common", "events", "decisions", "missions")
CREATES = re.compile(r"(?m)^[^#\n]*\bsubject_type\s*=\s*(princedom|senior_udil)\b")


def scan(files):
    found = {}
    for name, text in files.items():
        types = set(CREATES.findall(text))
        if types:
            found[name] = types
    return found


def script_files():
    files = {}
    for directory in SCRIPT_DIRS:
        for path in (ROOT / directory).rglob("*.txt"):
            files[path.relative_to(ROOT).as_posix()] = path.read_text(encoding="utf-8-sig", errors="replace")
    return files


def check(files, doc):
    failures = []
    found = scan(files)
    for name in sorted(set(found) | set(CREATION_PATHS)):
        if found.get(name) != CREATION_PATHS.get(name):
            failures.append(f"{name}: creates {sorted(found.get(name, ()))}, registry says {sorted(CREATION_PATHS.get(name, ()))}")
        if name in CREATION_PATHS and Path(name).name not in doc:
            failures.append(f"{name}: not mentioned in docs/KYIV_SUBJECT_FORMS.uk.md")
    adders = {
        name for name, text in files.items()
        if re.search(r"(?m)^[^#\n]*\bname\s*=\s*rip_held_as_an_udil\b", text)
    }
    if adders != HELD_AS_AN_UDIL_ADDED_IN:
        failures.append(f"rip_held_as_an_udil is added in {sorted(adders)}, registry says {sorted(HELD_AS_AN_UDIL_ADDED_IN)}")
    return failures


def main():
    doc = read("docs/KYIV_SUBJECT_FORMS.uk.md")
    files = script_files()
    failures = check(files, doc)

    for subject in ("princedom", "senior_udil"):
        assert len(re.findall(rf"(?m)^{subject} = \{{", "".join(
            p.read_text(encoding="utf-8-sig") for p in (ROOT / "common/subject_types").glob("RIP_*.txt")))) == 1, subject
    statehood = read("localisation/RIP_shared_ruthenian_statehood_l_english.yml")
    for subject in ("princedom", "senior_udil"):
        for suffix in ("_title", "_title_plural", "_long_desc", "_is_our"):
            assert f" {subject}{suffix}:" in statehood, subject + suffix
    assert 'princedom_is_our:0 "$NAME|Y$ is our princedom."' in statehood
    assert "мертва" in doc, "the document must keep saying that the trade-city route does not fire"

    assert not failures, "\n".join(failures)

    # Planted violations: a new creation path, a vanished path, a new modifier site.
    extra = dict(files)
    extra["events/RIP_planted.txt"] = "option = {\n\tcreate_subject = {\n\t\tsubject_type = princedom\n\t}\n}\n"
    assert check(extra, doc), "a new princedom creation path was not caught"
    missing = {k: v for k, v in files.items() if k != "events/RIP_KIE_kyiv_independence.txt"}
    assert check(missing, doc), "a vanished creation path was not caught"
    extra = dict(files)
    extra["decisions/RIP_planted.txt"] = "effect = {\n\tadd_country_modifier = {\n\t\tname = rip_held_as_an_udil\n\t}\n}\n"
    assert check(extra, doc), "a new rip_held_as_an_udil site was not caught"
    commented = dict(files)
    commented["decisions/RIP_planted.txt"] = "# subject_type = senior_udil\n"
    assert not check(commented, doc), "a commented-out creation was counted"

    print(f"PASS: {len(CREATION_PATHS)} udil creation paths match the registry and docs/KYIV_SUBJECT_FORMS.uk.md (static only)")


if __name__ == "__main__":
    main()
