"""Every reform id that a custom localisation tests must be a reform that exists.

EU4 never complains about `has_reform = <id>` when no such reform exists: the trigger is simply never true, the rule
under it is dead and the country falls through to a later rule. The first parliament-name ladder tested
chr_siversk_veche_reform (the reform is siversk_veche_reform), and so did the test that held it, so everything stayed
green while the Siversk Veche was never named. This check reads every customizable_localization/*.txt and resolves
each has_reform id:

  - defined in the mod's common/government_reforms/*.txt: fine;
  - an installed EU4 of the target version is found: the id must be defined by the mod or by vanilla;
  - no install: a vanilla id cannot be told from a typo, so only an id that starts with one of the mod's own prefixes
    (RIP_PREFIXES) is judged. Every other id is reported as unverified and never fails.

The matcher and the judgement are run on planted text first, so a pattern that stops matching cannot turn the check
into a silent pass.
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path

from clausewitz_testlib import ROOT, _mask_comments_and_strings, line_number, vanilla_root

# Prefixes that only the mod uses, so an id that carries one and is not defined in common/government_reforms is a typo
# even when there is no EU4 install to ask (main() checks the claim against the install when there is one). Never add
# a prefix that vanilla also uses: ruthenian_tsardom is vanilla's own reform, and a ruthenian_ entry would call it a typo.
RIP_PREFIXES = ("chr_", "hlc_", "vln_", "pdl_", "uzh_", "lit_", "zaz_", "het_", "prl_", "plt_", "kyivan_", "rip_")
HAS_REFORM = re.compile(r'\bhas_reform\s*=\s*"?([A-Za-z0-9_]+)')


def top_level_names(text: str) -> list[str]:
    """Names of the `name = { ... }` blocks at depth 0 of one script file: the reforms that file defines."""
    names, depth = [], 0
    for token in re.finditer(r"[{}]|([A-Za-z0-9_]+)\s*=\s*\{", _mask_comments_and_strings(text)):
        if token[0] == "}":
            depth -= 1
            continue
        if token[1] and depth == 0:
            names.append(token[1])
        depth += 1
    return names


def defined_reforms(folder: Path) -> set[str]:
    names: set[str] = set()
    for path in sorted(folder.glob("*.txt")):        # common/ is flat: EU4 reads no subfolder of it
        names.update(top_level_names(path.read_text(encoding="utf-8-sig", errors="replace")))
    return names


def references(text: str) -> list[tuple[str, int]]:
    """(id, line) of every has_reform in one custom-localisation file. Comments are blanked, lines are kept."""
    text = re.sub(r"#[^\n]*", lambda match: " " * len(match.group()), text)
    return [(match[1], line_number(text, match.start())) for match in HAS_REFORM.finditer(text)]


def judge(ident: str, mod_ids: set[str], vanilla_ids: set[str] | None) -> str:
    """'ok', 'missing' (known not to exist) or 'unverified' (vanilla may define it and nothing here can say)."""
    if ident in mod_ids:
        return "ok"
    if vanilla_ids is not None:
        return "ok" if ident in vanilla_ids else "missing"
    return "missing" if ident.startswith(RIP_PREFIXES) else "unverified"


def selftest() -> None:
    """Plant the original typo: if the matcher or the judgement stops seeing it, fail before anything is scanned."""
    mod = {"siversk_veche_reform", "chr_desna_staple_reform"}
    planted = (
        "# has_reform = chr_in_a_comment_is_not_read\n"
        "text = { trigger = { has_reform = chr_siversk_veche_reform } }\n"
        'text = { trigger = { OR = { has_reform = siversk_veche_reform has_reform = "chr_quoted_typo" } } }\n'
    )
    found = references(planted)
    assert found == [("chr_siversk_veche_reform", 2), ("siversk_veche_reform", 3), ("chr_quoted_typo", 3)], found
    assert [judge(ident, mod, None) for ident, _ in found] == ["missing", "ok", "missing"]
    assert judge("cossacks_reform", mod, None) == "unverified"           # may be vanilla's: never a failure on its own
    assert judge("cossacks_reform", mod, {"cossacks_reform"}) == "ok"
    assert judge("cossacks_reform", mod, {"other_reform"}) == "missing"  # an install that lacks it can say so
    assert difflib.get_close_matches("chr_siversk_veche_reform", sorted(mod), n=1) == ["siversk_veche_reform"]
    assert top_level_names("a = { b = { } c = yes }\n# d = { }\nelist = { { x = { } } }\ne = { }") == ["a", "elist", "e"]


def main() -> int:
    selftest()
    mod_ids = defined_reforms(ROOT / "common/government_reforms")
    install = vanilla_root()
    vanilla_ids = (defined_reforms(install / "common/government_reforms") or None) if install else None
    clash = sorted(ident for ident in vanilla_ids or () if ident.startswith(RIP_PREFIXES))
    assert not clash, f"vanilla defines reform(s) with a mod prefix, so RIP_PREFIXES would mislabel them: {clash}"
    files =sorted((ROOT / "customizable_localization").glob("*.txt"))
    assert mod_ids and files, "common/government_reforms or customizable_localization is empty: nothing would be checked"

    failures: list[str] = []
    unverified: dict[str, str] = {}
    counts = {"ok": 0, "missing": 0, "unverified": 0}
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        for ident, line in references(path.read_text(encoding="utf-8-sig", errors="replace")):
            verdict = judge(ident, mod_ids, vanilla_ids)
            counts[verdict] += 1
            if verdict == "missing":
                hint = difflib.get_close_matches(ident, sorted(mod_ids), n=1)
                failures.append(f"{name}:{line}: has_reform = {ident} names no reform"
                                + (f" (did you mean {hint[0]}?)" if hint else ""))
            elif verdict == "unverified":
                unverified.setdefault(ident, f"{name}:{line}")
    total = sum(counts.values())
    assert total, "no has_reform found in customizable_localization: the matcher or the folder is wrong"

    if failures:
        where = "common/government_reforms" + (" or in the installed EU4" if vanilla_ids else "")
        print(f"{len(failures)} has_reform id(s) in customizable_localization are not defined in {where}:")
        print("\n".join("  " + failure for failure in failures))
        return 1
    if unverified:
        print(f"SKIP: {len(unverified)} id(s) are not the mod's, so only an installed EU4 can verify them (EU4_DIR): "
              + ", ".join(sorted(unverified)))
    print(f"PASS: {total} has_reform ids in {len(files)} customizable_localization files, "
          f"{counts['ok']} defined, {counts['unverified']} unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
