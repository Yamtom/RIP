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

def is_mostly_latin(line):
    """\u041A\u0438\u0440\u0438\u043B\u0438\u0446\u044F \u0432 \u0440\u044F\u0434\u043A\u0443 - \u0449\u0435 \u043D\u0435 \u043F\u0435\u0440\u0435\u043A\u043B\u0430\u0434 \u0440\u044F\u0434\u043A\u0430.

    \u041C\u0430\u0441\u043E\u0432\u0430 \u0437\u0430\u043C\u0456\u043D\u0430 \u0441\u043B\u0456\u0432 \u043B\u0438\u0448\u0438\u043B\u0430 \u043F\u043E \u0434\u043E\u043A\u0443\u043C\u0435\u043D\u0442\u0430\u0445 \u0440\u0435\u0447\u0435\u043D\u043D\u044F \u043D\u0430 \u043A\u0448\u0442\u0430\u043B\u0442 \u00AB\u0412\u043E\u043B\u043E\u0434\u0456\u0454 steppe
    provinces with Ruthenian culture\u00BB \u0442\u0430 \u00ABthe design target is 25 \u0440\u043E\u043A\u0456\u0432\u00BB: \u043E\u0434\u043D\u0435
    \u0443\u043A\u0440\u0430\u0457\u043D\u0441\u044C\u043A\u0435 \u0441\u043B\u043E\u0432\u043E \u0432\u0441\u0435\u0440\u0435\u0434\u0438\u043D\u0456 \u0430\u043D\u0433\u043B\u0456\u0439\u0441\u044C\u043A\u043E\u0457 \u0444\u0440\u0430\u0437\u0438, \u0456 \u043F\u0435\u0440\u0435\u0432\u0456\u0440\u043A\u0430 \u043D\u0430 \u0441\u0430\u043C\u0443 \u043B\u0438\u0448\u0435
    \u043A\u0438\u0440\u0438\u043B\u0438\u0446\u044E \u0437\u0430\u0440\u0430\u0445\u043E\u0432\u0443\u0432\u0430\u043B\u0430 \u0457\u0445 \u044F\u043A \u043F\u0435\u0440\u0435\u043A\u043B\u0430\u0434\u0435\u043D\u0456. \u041A\u043E\u0434 \u0443 \u0437\u0432\u043E\u0440\u043E\u0442\u043D\u0438\u0445 \u043B\u0430\u043F\u043A\u0430\u0445 \u0456 \u0430\u0434\u0440\u0435\u0441\u0438
    \u043F\u043E\u0441\u0438\u043B\u0430\u043D\u044C \u043D\u0435 \u0440\u0430\u0445\u0443\u0454\u043C\u043E - \u0446\u0435 \u043D\u0435 \u043F\u0440\u043E\u0437\u0430.
    """
    bare = re.sub(r"`[^`]*`", " ", line)
    bare = re.sub(r"\]\([^)]*\)", " ", bare)
    lat = sum(1 for c in bare if 'a' <= c.lower() <= 'z')
    cyr = sum(1 for c in bare if '\u0400' <= c <= '\u04FF')
    return lat >= 40 and lat >= 3 * cyr

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
    # рядки промпта до генератора зображень: підпис український, тіло навмисне
    # англійське, бо його читає не людина
    if s.startswith(("- Призначення:", "- Нотатки про стиль:")):
        return False
    # «- `280` -> збережено: ...; прибрано: ...» - це перелік ігрових назв
    # провінцій, а не проза
    if re.match(r"^- `\d+` -> (збережено|прибрано)", s):
        return False
    # рядок таблиці модифікаторів: «| `id` | ефекти | тривалість | подія |».
    # Стовпчик ефектів - це терміни EU4, а остання клітинка - ідентифікатор;
    # перекладати нема чого. Якщо в останній клітинці проза, рядок лишається.
    if re.match(r"^\|\s*`[a-z_0-9]+`\s*\|.*\|\s*`?[a-z_0-9]+\.[0-9a-z.]+`?[a-z ]*\s*\|$", s):
        return False
    # власна назва мода, як її записано в descriptor.mod
    if s.lstrip("# ") == "Alternative Ruthenian Immersion Pack":
        return False
    if not re.search(r"[A-Za-z\u0400-\u04FF]{3,}", s):
        return False
    return True

LIST = "--list" in sys.argv          # показати самі неперекладені рядки
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

# docs/ is not the whole of it: the front page and the two harness readmes are
# documentation too, and being outside docs/ is exactly how they stayed English
# through the translation pass.
TRACKED = sorted(glob.glob("docs/*.md")) + [
    "README.md",
    os.path.join("tests", "dev_tools", "README.md"),
    os.path.join("tests", "observer", "README.md"),
]

rows = []
for path in TRACKED:
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
        if is_cyrillic(line) and not is_mostly_latin(line):
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
