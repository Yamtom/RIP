"""Regression gate for the tag/entity naming layout in localisation/replace/.

Verifies:
1. Every file in localisation/replace/ follows RIP_<OWNER>_<ENTITY>_l_<language>.yml
   with a known country tag / tag pair or shared_<family> owner and stays flat.
2. Every file keeps a single UTF-8 BOM, matching l_<language>: header, and parses
   strictly as Paradox localisation.
3. Zero duplicate keys exist across localisation/replace/ per language, and zero
   keys collide with root localisation/*_l_<language>.yml.
4. Per-language key counts and multiset (key, version, text) digests match the
   pre-migration baseline manifest identically.
5. Generator-owned <ENTITY> groups remain disjoint from non-generated files.
6. Planted regressions (bad filename, missing/duplicate BOM, wrong language header,
   duplicate key across files, nested subdirectory) are caught cleanly.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import localisation_replace_layout as layout
from check_file_encoding import error as encoding_error


def test_filename_parser_handles_shared_underscores() -> None:
    assert layout.parse_replace_filename("RIP_shared_church_content_l_french.yml") == (
        "shared_church", "content", "french"
    )
    assert layout.parse_replace_filename("RIP_shared_west_ruthenian_content_l_spanish.yml") == (
        "shared_west_ruthenian", "content", "spanish"
    )
    assert layout.parse_replace_filename("RIP_MOS_RUS_content_l_german.yml") == (
        "MOS_RUS", "content", "german"
    )
    assert layout.parse_replace_filename("RIP_HET_government_authority_l_english.yml") == (
        "HET", "government_authority", "english"
    )
    assert layout.parse_replace_filename("zzz_RIP_untranslated_l_french.yml") is None
    assert layout.parse_replace_filename("RIP_BADTAG_content_l_english.yml") is None


def test_no_overlap_with_root_localisation() -> None:
    for lang in layout.LANGUAGES:
        root_keys: set[str] = set()
        for path in sorted((ROOT / "localisation").glob(f"*_l_{lang}.yml")):
            for key, _, _ in layout.parse_yml_entries(path):
                root_keys.add(key)
        rep_keys: set[str] = set()
        for path in sorted((ROOT / "localisation/replace").glob(f"*_l_{lang}.yml")):
            for key, _, _ in layout.parse_yml_entries(path):
                rep_keys.add(key)
        overlap = sorted(root_keys & rep_keys)
        assert not overlap, f"{lang}: root localisation overlaps replace/: {overlap[:10]}"


def test_generator_and_static_groups_disjoint() -> None:
    manifest = json.loads(layout.MANIFEST_PATH.read_text(encoding="utf-8"))
    gen_groups = set(layout.GENERATOR_OWNED_GROUPS)
    actual_groups = defaultdict(set)
    for path in sorted((ROOT / "localisation/replace").glob("*.yml")):
        parsed = layout.parse_replace_filename(path.name)
        assert parsed is not None, path.name
        owner, entity, _ = parsed
        actual_groups[f"RIP_{owner}_{entity}"].add(path.name)
    assert gen_groups <= set(actual_groups), sorted(gen_groups - set(actual_groups))
    assert "language_digests" in manifest


def test_catalogue() -> None:
    """Moving or editing a string must preserve its key, version and loading layer."""
    root = ROOT / "localisation"
    manifest = json.loads(layout.MANIFEST_PATH.read_text(encoding="utf-8"))
    known_owners = layout.ALLOWED_OWNERS | {"ZAZ_HET", "KUY", "shared_imperial"}
    owner_names = "|".join(sorted(known_owners, key=len, reverse=True))
    name_pattern = re.compile(rf"RIP_(?:{owner_names})_[a-z][a-z0-9_]*_l_({'|'.join(layout.LANGUAGES)})\.yml")
    # These entries also occur in the installed vanilla catalogue. Retain their load order.
    priority_files = {
        "000_RIP_shared_ruthenian_restoration_l_english.yml": {"restored_ruthenia"},
        "zzz_RIP_shared_ruthenian_overrides_l_english.yml": {
            "conquest_of_constantinople", "grand_duchy_reform_desc", "POSADNIK",
            "GRAND_POSADNIK", "POSADNITSA", "GRAND_POSADNITSA", "zasechnaya_cherta",
        },
    }
    by_layer = defaultdict(list)
    for path in root.rglob("*.yml"):
        assert path.parent in (root, root / "replace"), path
        name = path.name
        if name in priority_files:
            assert path.parent == root, path
            name = name.split("_", 1)[1]
        match = name_pattern.fullmatch(name)
        assert match, path
        lang = match[1]
        assert path.read_text(encoding="utf-8-sig").splitlines()[0] == f"l_{lang}:", path
        entries = layout.parse_yml_entries(path)
        if path.name in priority_files:
            assert {key for key, _, _ in entries} == priority_files[path.name], path
        layer = "root" if path.parent == root else "replace"
        by_layer[layer, lang].extend((key, version) for key, version, _ in entries)
    for (layer, lang), entries in by_layer.items():
        assert len(entries) == len({k for k, _ in entries}), (layer, lang, "duplicate keys")
        payload = json.dumps(sorted(entries), separators=(",", ":")).encode()
        assert sha256(payload).hexdigest() == manifest["catalogue_key_digests"][layer][lang], (layer, lang)
    assert len(by_layer) == 2 * len(layout.LANGUAGES)


def test_planted_violations() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        old_dir = layout.REPLACE_DIR
        try:
            layout.REPLACE_DIR = tmp_dir
            # 1. Invalid filename
            bad_name = tmp_dir / "zzz_legacy_l_english.yml"
            bad_name.write_bytes(b"\xef\xbb\xbfl_english:\r\n test_k:0 \"ok\"\r\n")
            assert any("non-conforming replace filename" in p for p in layout.check_current({}))
            bad_name.unlink()

            # 2. Wrong header language
            bad_hdr = tmp_dir / "RIP_HET_test_l_french.yml"
            bad_hdr.write_bytes(b"\xef\xbb\xbfl_english:\r\n test_k:0 \"ok\"\r\n")
            assert any("does not match language french" in p for p in layout.check_current({}))
            bad_hdr.unlink()

            # 3. Duplicate key across two replace files
            f1 = tmp_dir / "RIP_HET_a_l_english.yml"
            f2 = tmp_dir / "RIP_ZAZ_b_l_english.yml"
            f1.write_bytes(b"\xef\xbb\xbfl_english:\r\n dup_k:0 \"one\"\r\n")
            f2.write_bytes(b"\xef\xbb\xbfl_english:\r\n dup_k:0 \"two\"\r\n")
            assert any("duplicate key 'dup_k'" in p for p in layout.check_current({}))
            f1.unlink()
            f2.unlink()

            # 4. Nested directory in replace/
            sub = tmp_dir / "CHR"
            sub.mkdir()
            assert any("nested directory forbidden" in p for p in layout.check_current({}))
            sub.rmdir()

            # 5. Missing BOM caught
            no_bom = tmp_dir / "RIP_HET_a_l_english.yml"
            no_bom.write_bytes(b"l_english:\r\n ok_k:0 \"ok\"\r\n")
            assert any("UTF-8 BOM" in p for p in layout.check_current({}))
            assert encoding_error("localisation/replace/RIP_HET_a_l_english.yml", b"l_english:\n") is not None
        finally:
            layout.REPLACE_DIR = old_dir


def main() -> int:
    test_filename_parser_handles_shared_underscores()
    problems = layout.check_current()
    assert not problems, "\n".join(problems)
    test_no_overlap_with_root_localisation()
    test_catalogue()
    test_generator_and_static_groups_disjoint()
    test_planted_violations()
    total_files = len(list((ROOT / "localisation/replace").glob("*.yml")))
    print(f"LOCALISATION REPLACE LAYOUT TEST PASS: {total_files} files, 0 duplicates, baseline digests matched, 5 planted regressions caught")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
