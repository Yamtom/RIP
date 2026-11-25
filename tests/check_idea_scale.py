"""Шкала національних ідей мода не виходить за ванільний максимум одного слота.

Запуск з кореня мода:  python tests/check_idea_scale.py

Для кожного модифікатора в наборах мода (common/ideas/01_*.txt і
zzz_RIP_group_ideas.txt) береться найбільше значення, яке ваніль 1.37.5 дає за
одну ідею, традицію чи амбіцію в 00_country_ideas.txt і zz_group_ideas.txt.
Бонус, сильніший за цей максимум, - помилка (так колись прослизнули
administrative_efficiency = 0.2 і discipline = 0.1 у VLN).

Штраф не рахується: якщо ваніль має модифікатор лише з одним знаком
(culture_conversion_cost тільки від'ємний), значення з протилежним знаком є
свідомою ціною ідеї й не перевіряється. Модифікатори, яких ваніль у наборах
ідей не має, вважаються помилкою (FAIL), щоб мертві чи неванільні ключі
не прослизали непоміченими.
"""
import io
import re
import sys
from collections import defaultdict

from clausewitz_testlib import ROOT, vanilla_root

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = re.compile(r'"[^"]*"|[{}=<>]|[^\s{}=<>"#]+|#[^\n]*')
SKIP_SLOTS = {"trigger", "free", "ai_will_do", "category", "important"}


def parse(text):
    tokens = [t for t in TOKEN.findall(text) if not t.startswith("#")]
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(tokens):
            key = tokens[pos]
            if key == "}":
                pos += 1
                return out
            if pos + 1 < len(tokens) and tokens[pos + 1] in ("=", "<", ">"):
                pos += 2
                if pos < len(tokens) and tokens[pos] == "{":
                    pos += 1
                    out.append((key, block()))
                else:
                    out.append((key, tokens[pos] if pos < len(tokens) else None))
                    pos += 1
            else:
                pos += 1
        return out

    return block()


def read(path):
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", "replace")


def modifiers(path):
    for group, body in parse(read(path)):
        if not isinstance(body, list):
            continue
        for slot, content in body:
            if slot in SKIP_SLOTS or not isinstance(content, list):
                continue
            for name, value in content:
                try:
                    yield group, slot, name, float(value)
                except (TypeError, ValueError):
                    pass


def check_text_against_scale(filename, text, top, bottom):
    errors = []
    for group, body in parse(text):
        if not isinstance(body, list):
            continue
        for slot, content in body:
            if slot in SKIP_SLOTS or not isinstance(content, list):
                continue
            for modifier, raw_val in content:
                try:
                    value = float(raw_val)
                except (TypeError, ValueError):
                    continue
                if modifier not in top and modifier not in bottom:
                    errors.append(
                        f"{filename}: {group}.{slot} {modifier} = {value:g}"
                        " (модифікатора немає у ванільних наборах ідей)"
                    )
                    continue
                if value > 0 and top[modifier] > 0 and value > top[modifier]:
                    errors.append(
                        f"{filename}: {group}.{slot} {modifier} = {value:g}"
                        f" > ванільний максимум {top[modifier]:g}"
                    )
                if value < 0 and bottom[modifier] < 0 and value < bottom[modifier]:
                    errors.append(
                        f"{filename}: {group}.{slot} {modifier} = {value:g}"
                        f" < ванільний мінімум {bottom[modifier]:g}"
                    )
    return errors


def check_planted_unknown_and_overscale(top, bottom):
    planted_bad = """
    test_ideas = {
        start = { yearly_authority = 0.15 }
        slot_1 = { discipline = 0.1 }
    }
    """
    errs = check_text_against_scale("planted_bad.txt", planted_bad, top, bottom)
    assert any("yearly_authority" in e for e in errs), errs
    assert any("discipline" in e for e in errs), errs

    planted_ok = """
    test_ideas = {
        start = { siege_ability = -0.15 }
        slot_1 = { culture_conversion_cost = 0.5 }
    }
    """
    ok_errs = check_text_against_scale("planted_ok.txt", planted_ok, top, bottom)
    assert not ok_errs, ok_errs


def main():
    vanilla = vanilla_root()
    if vanilla is None:
        print("SKIP: no EU4 1.37.5 install, nothing to measure the idea scale against")
        return 0

    top = defaultdict(float)
    bottom = defaultdict(float)
    for name in ("00_country_ideas.txt", "zz_group_ideas.txt"):
        for _, _, modifier, value in modifiers(vanilla / "common" / "ideas" / name):
            top[modifier] = max(top[modifier], value)
            bottom[modifier] = min(bottom[modifier], value)

    check_planted_unknown_and_overscale(top, bottom)

    files = sorted((ROOT / "common" / "ideas").glob("01_*.txt"))
    files += sorted((ROOT / "common" / "ideas").glob("zzz_*.txt"))
    errors = []
    for path in files:
        errors.extend(check_text_against_scale(path.name, read(path), top, bottom))

    for line in errors:
        print("FAIL:", line)
    if errors:
        return 1
    print(f"PASS: {len(files)} файлів ідей у межах ванільної шкали одного слота")
    return 0


if __name__ == "__main__":
    sys.exit(main())
