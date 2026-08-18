"""Скільки документації вже українською.

Запуск з кореня мода:  python tests/check_docs_language.py

Рахує лише прозу. Рядки, які мають лишатися англійськими - код, таблиці з
самими ідентифікаторами, шляхи, посилання, промпти для генератора зображень і
BBCode вітрини Steam - до знаменника не потрапляють, бо їх перекладати не
треба й ніколи не буде «100%».
"""
import glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def is_cyrillic(line):
    return any('\u0400' <= c <= '\u04FF' for c in line)

def is_translatable(line, in_code):
    s = line.strip()
    if in_code or not s:
        return False
    # службові й неперекладні рядки
    if s.startswith(("```", "|---", "---", ">", "#!", "http")):
        return False
    # рядок без прози: приберемо код у зворотних лапках, посилання й розмітку -
    # якщо не лишилось жодного слова з трьох літер, перекладати нема чого
    # заголовок, що складається з одного ідентифікатора (ключ ресурсу тощо)
    if re.match(r"^#+\s+[A-Za-z0-9_.:/-]+$", s):
        return False
    # рядок таблиці правопису: «вживати | не вживати | 24 : 0» - самі форми й числа
    if re.match(r"^\|[^|]+\|[^|]+\|\s*\d+\s*:\s*\d+\s*\|$", s):
        return False
    bare = re.sub(r"`[^`]*`", " ", s)
    bare = re.sub(r"\]\([^)]*\)", " ", bare)
    bare = re.sub(r"[-*+#>|:.,()\[\]/\_=]", " ", bare)
    if not re.search(r"[A-Za-zЀ-ӿ]{3,}", bare):
        return False
    if re.match(r"^\|[\s`|A-Za-z0-9_./:+-]*\|$", s) and not re.search(r"[A-Za-z]{4,}\s+[A-Za-z]{4,}", s):
        return False                                    # таблиця самих ID
    if "Prompt (англійською)" in s or s.startswith("- Промпт"):
        return False
    if not re.search(r"[A-Za-z\u0400-\u04FF]{3,}", s):
        return False
    return True

LIST = "--list" in sys.argv          # показати самі неперекладені рядки
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

rows = []
for path in sorted(glob.glob("docs/*.md")):
    if ONLY and not any(o in path for o in ONLY):
        continue
    text = io.open(path, encoding="utf-8", errors="replace").read().split("\n")
    in_code = False
    total = uk = 0
    for line in text:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not is_translatable(line, in_code):
            continue
        total += 1
        if is_cyrillic(line):
            uk += 1
        elif LIST:
            print(f"{path}| {line.rstrip()}")
    if total:
        rows.append((uk * 100 // total, uk, total, os.path.basename(path)))

rows.sort()
for pct, uk, total, name in rows:
    bar = "#" * (pct // 5) + "." * (20 - pct // 5)
    print(f"  {pct:3d}%  [{bar}]  {name}  ({uk}/{total})")

tu = sum(r[1] for r in rows)
tt = sum(r[2] for r in rows)
print(f"\n  Разом: {tu}/{tt} перекладних рядків українською ({tu * 100 // tt}%)")
