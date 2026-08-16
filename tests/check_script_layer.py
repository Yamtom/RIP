"""Structural checks over the mod's script layer.

Run from the mod root:  python tests/check_script_layer.py
Exit code 1 if anything is broken, so it can gate a merge.

The mod inherits a great deal from vanilla - localisation above all - so a
check that only reads this repository reports hundreds of things as missing
when the game would resolve them. Point EU4_DIR at the install to get a true
answer; without it the localisation checks are skipped rather than guessed at.

    set EU4_DIR=D:\\...\\steamapps\\common\\Europa Universalis IV
"""
import re, glob, io, sys, os, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIRS = ["events", "common", "missions", "decisions",
               "customizable_localization", "history", "interface"]

EU4_CANDIDATES = [
    os.environ.get("EU4_DIR"),
    r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV",
]
EU4_DIR = next((d for d in EU4_CANDIDATES
                if d and os.path.isdir(os.path.join(d, "localisation"))), None)

# --- helpers ---------------------------------------------------------------

def read(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw

def decode(raw):
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", "replace"), True
    try:
        return raw.decode("utf-8"), False
    except UnicodeDecodeError:
        return raw.decode("cp1252", "replace"), False

def uncomment(text):
    """Blank out # comments only. Quoted strings are kept, because script
    refers to modifiers and localisation keys both quoted and bare."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "#":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)

def strip_comments(text):
    """Blank out # comments and "quoted strings" so brace counting is honest.
    Only safe for counting braces - use uncomment() when reading values."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "#":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
        elif c == '"':
            out.append(" ")
            i += 1
            while i < n and text[i] != '"':
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append(" ")
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)

def script_files():
    for d in SCRIPT_DIRS:
        for path in glob.glob(os.path.join(d, "**", "*.txt"), recursive=True):
            yield path.replace("\\", "/")

def loc_files():
    for path in glob.glob(os.path.join("localisation", "**", "*.yml"), recursive=True):
        yield path.replace("\\", "/")

errors, warnings = [], []
def err(msg):  errors.append(msg)
def warn(msg): warnings.append(msg)

# --- 1. encoding + brace balance ------------------------------------------

for path in script_files():
    raw = read(path)
    if raw.startswith(b"\xef\xbb\xbf"):
        err(f"{path}: UTF-8 BOM on a .txt script file (EU4 wants none)")
    text, _ = decode(raw)
    stripped = strip_comments(text)
    depth, line = 0, 1
    bad = None
    for ch in stripped:
        if ch == "\n":
            line += 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0 and bad is None:
                bad = line
                depth = 0
    if bad is not None:
        err(f"{path}:{bad}: unmatched closing brace")
    if depth != 0:
        err(f"{path}: {depth} unclosed opening brace(s)")

for path in loc_files():
    raw = read(path)
    if not raw.startswith(b"\xef\xbb\xbf"):
        err(f"{path}: localisation .yml is missing its required UTF-8 BOM")

# --- 2. localisation index -------------------------------------------------

LOC_ENTRY = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"', re.M)
loc_keys = collections.defaultdict(set)   # language -> keys
for path in loc_files():
    text, _ = decode(read(path))
    lang = "english"
    m = re.search(r"_l_([a-z]+)\.yml$", path)
    if m:
        lang = m.group(1)
    for key in LOC_ENTRY.findall(text):
        loc_keys[lang].add(key)
english = loc_keys["english"]

# Vanilla keys the game will resolve even though this repository has no copy.
vanilla_english = set()
if EU4_DIR:
    for path in glob.glob(os.path.join(EU4_DIR, "localisation", "**", "*.yml"),
                          recursive=True):
        if "_l_english" not in os.path.basename(path):
            continue
        text, _ = decode(read(path))
        vanilla_english.update(LOC_ENTRY.findall(text))
    english = english | vanilla_english

# --- 3. events: ids, namespaces, loc coverage, orphan chains --------------

EVENT_BLOCK = re.compile(
    r"^(country_event|province_event)\s*=\s*\{", re.M)

event_ids = {}                    # id -> (path, line)
triggered_only = {}               # id -> (path, line)
fired_ids = set()                 # ids referenced by country_event = { id = X }
missing_loc = []

for path in script_files():
    if not path.startswith("events/"):
        continue
    text, _ = decode(read(path))
    body = uncomment(text)
    namespaces = set(re.findall(r"^\s*namespace\s*=\s*(\S+)", body, re.M))

    # slice the file into top-level event blocks
    for m in EVENT_BLOCK.finditer(body):
        start = m.end() - 1
        depth, i = 0, start
        while i < len(body):
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = body[start:i + 1]
        line = body.count("\n", 0, m.start()) + 1

        idm = re.search(r'^\s*id\s*=\s*"?([A-Za-z0-9_.\-]+)"?', block, re.M)
        if not idm:
            err(f"{path}:{line}: event block with no id")
            continue
        eid = idm.group(1)
        if eid in event_ids:
            p, l = event_ids[eid]
            err(f"{path}:{line}: duplicate event id {eid} (also {p}:{l})")
        event_ids[eid] = (path, line)

        ns = eid.rsplit(".", 1)[0]
        if namespaces and ns not in namespaces:
            err(f"{path}:{line}: event {eid} uses namespace '{ns}' "
                f"not declared in this file ({', '.join(sorted(namespaces))})")

        if re.search(r"^\s*is_triggered_only\s*=\s*yes", block, re.M):
            triggered_only[eid] = (path, line)

        # A hidden event never opens a window, so its text is never read.
        hidden = bool(re.search(r"^\s*hidden\s*=\s*yes", block, re.M))

        # loc keys used by this event
        for kw in ("title", "desc"):
            for km in re.finditer(rf'^\s*{kw}\s*=\s*"?([A-Za-z0-9_.\-]+)"?\s*$',
                                  block, re.M):
                key = km.group(1)
                if key not in english:
                    missing_loc.append((path, eid, key, hidden))
        for km in re.finditer(r'^\s*name\s*=\s*"?([A-Za-z0-9_.\-]+[._][a-z])"?\s*$',
                              block, re.M):
            key = km.group(1)
            if key not in english:
                missing_loc.append((path, eid, key, hidden))

# every `country_event = { id = X }` / `province_event = { id = X }` reference
for path in script_files():
    text, _ = decode(read(path))
    body = uncomment(text)
    for m in re.finditer(
            r'(?:country_event|province_event)\s*=\s*\{[^{}]*?\bid\s*=\s*"?([A-Za-z0-9_.\-]+)"?',
            body):
        fired_ids.add(m.group(1))

for eid, (path, line) in sorted(triggered_only.items()):
    if eid not in fired_ids:
        warn(f"{path}:{line}: {eid} is is_triggered_only but nothing fires it")

for path, eid, key, hidden in missing_loc:
    msg = f"{path}: event {eid} references missing localisation key '{key}'"
    if not EU4_DIR:
        warn(msg + " (unverified - EU4_DIR not set, may resolve from vanilla)")
    elif hidden:
        warn(msg + " (hidden event - never displayed)")
    else:
        err(msg)

# --- 4. modifiers: defined vs used vs localised ---------------------------

defined_modifiers = {}    # name -> path
for path in glob.glob("common/event_modifiers/*.txt"):
    path = path.replace("\\", "/")
    text, _ = decode(read(path))
    body = strip_comments(text)
    depth = 0
    for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\}", body):
        if m.group(0) == "}":
            depth -= 1
            continue
        if depth == 0:
            name = m.group(1)
            if name in defined_modifiers:
                err(f"{path}: modifier '{name}' redefined "
                    f"(first in {defined_modifiers[name]})")
            defined_modifiers[name] = path
        depth += 1

used_modifiers = set()
for path in script_files():
    text, _ = decode(read(path))
    body = uncomment(text)
    for m in re.finditer(
            r"add_(?:province|country|ruler|permanent_province)_modifier\s*=\s*\{"
            r"[^{}]*?\bname\s*=\s*\"?([A-Za-z0-9_]+)\"?", body):
        used_modifiers.add(m.group(1))
    for m in re.finditer(
            r"(?:remove_province_modifier|remove_country_modifier|"
            r"has_province_modifier|has_country_modifier)\s*=\s*\"?([A-Za-z0-9_]+)\"?",
            body):
        used_modifiers.add(m.group(1))

for name in sorted(defined_modifiers):
    if name not in used_modifiers:
        warn(f"{defined_modifiers[name]}: modifier '{name}' is defined but never used")
    if name not in english:
        err(f"{defined_modifiers[name]}: modifier '{name}' has no localisation")

# --- 5. province- vs country-scope modifier entries -----------------------

# Modifiers that only take effect in country scope. Putting one of these in a
# block applied with add_province_modifier is silently ignored by the game.
COUNTRY_ONLY = {
    "cavalry_power", "infantry_power", "artillery_power", "cavalry_cost",
    "infantry_cost", "artillery_cost", "cavalry_flanking", "land_morale",
    "naval_morale", "discipline", "manpower_recovery_speed", "global_manpower_modifier",
    "prestige", "legitimacy", "diplomatic_reputation", "advisor_cost",
    "vassal_income", "liberty_desire", "tolerance_heathen", "tolerance_heretic",
    "tolerance_own", "ae_impact", "unjustified_demands", "core_creation",
    "fort_maintenance_modifier", "hostile_attrition", "diplomats",
    "global_tax_modifier", "global_trade_power", "war_exhaustion",
    "army_tradition", "navy_tradition", "republican_tradition", "devotion",
    "horde_unity", "meritocracy", "global_unrest", "stability_cost_modifier",
    "development_cost", "years_of_nationalism", "production_efficiency",
    "num_accepted_cultures", "diplomatic_upkeep", "global_autonomy",
    "administrative_efficiency", "max_absolutism", "governing_capacity",
    "prestige_decay", "technology_cost", "trade_efficiency", "land_attrition",
}
# Modifiers that only take effect in province scope.
# Note: garrison_size is NOT here - it is valid in both scopes (Defensive ideas
# use it at country level).
PROVINCE_ONLY_PREFIX = ("local_",)
PROVINCE_ONLY = {
    "supply_limit_modifier", "province_trade_power_modifier",
    "trade_goods_size_modifier", "min_autonomy", "allowed_num_of_buildings",
    "regiment_recruit_speed", "block_introduce_institution",
}

def is_province_only(k):
    return k.startswith(PROVINCE_ONLY_PREFIX) or k in PROVINCE_ONLY

# classify every defined modifier by how it is actually applied
applied_as = collections.defaultdict(set)   # modifier -> {"province","country"}
for path in script_files():
    text, _ = decode(read(path))
    body = uncomment(text)
    for kind in ("province", "country", "permanent_province"):
        for m in re.finditer(
                rf"add_{kind}_modifier\s*=\s*\{{[^{{}}]*?\bname\s*=\s*\"?([A-Za-z0-9_]+)\"?",
                body):
            applied_as[m.group(1)].add(
                "province" if "province" in kind else "country")

for path in glob.glob("common/event_modifiers/*.txt"):
    path = path.replace("\\", "/")
    text, _ = decode(read(path))
    body = strip_comments(text)
    for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*\{(.*?)^\}", body, re.M | re.S):
        name, inner = m.group(1), m.group(2)
        line0 = body.count("\n", 0, m.start()) + 1
        scopes = applied_as.get(name, set())
        if len(scopes) != 1:
            continue   # unused, or genuinely applied both ways
        scope = next(iter(scopes))
        for km in re.finditer(r"^\s*([a-z_0-9]+)\s*=", inner, re.M):
            key = km.group(1)
            kline = line0 + inner.count("\n", 0, km.start())
            if scope == "province" and key in COUNTRY_ONLY:
                err(f"{path}:{kline}: '{name}' is applied with "
                    f"add_province_modifier but sets country-scope '{key}' "
                    f"(silently ignored in game)")
            if scope == "country" and is_province_only(key):
                err(f"{path}:{kline}: '{name}' is applied with "
                    f"add_country_modifier but sets province-scope '{key}' "
                    f"(silently ignored in game)")

# --- 6. province ids against the name written beside them ------------------

# The border principalities chain shipped with every province id wrong while
# every comment named the right place, so the comments are worth checking.
if EU4_DIR:
    province_name = {}
    for d in (os.path.join(EU4_DIR, "history", "provinces"),
              os.path.join("history", "provinces")):     # mod overrides win
        for path in glob.glob(os.path.join(d, "*.txt")):
            m = re.match(r"(\d+)\s*-\s*(.+)\.txt$", os.path.basename(path))
            if m:
                province_name[int(m.group(1))] = m.group(2).strip()

    # The mod deliberately writes Ukrainian toponyms where Paradox writes
    # Russian or Polish ones - see docs/STYLE_GLOSSARY.md section 1. Those are
    # the house style, not mistakes, so they must not be reported.
    ALIASES = [
        {"kyiv", "kiev"},
        {"chernihiv", "chernigov", "chernihov"},
        {"lviv", "lwow", "lvov", "lemberg"},
        {"kharkiv", "kharkov"},
        {"halych", "halicz", "galich"},
        {"kamianets", "kamienec", "kamieniec", "kamenets"},
        {"podillia", "podolia", "kamienec"},     # Kamianets is Podillia's seat
        {"volhynia", "volyn"},
        {"bratslav", "braclaw"},
        {"zaporozhia", "zaporizhia", "zaporizhzhia", "zaporozhie"},
        {"moskva", "moscow"},
        {"vilnius", "wilno", "vilna", "lithuania"},  # 272's capital is Vilnius
        {"krakow", "cracow"},
        {"novgorodseversky", "novhorodsiversky", "novhorod", "siversky"},
        {"yedisan", "ochakov", "ochakiv"},        # Ochakiv is Yedisan's port
        {"maramaros", "maramures", "mukachevo"},
        {"pest", "buda"},
        {"kasimov", "qasim"},
        {"odesa", "odessa"},
        {"pereiaslav", "pereyaslav"},
        {"theodoro", "blacksea"},   # Theodoro is on the Black Sea coast
    ]

    def looks_like(comment, name):
        """Loose match - the comment is prose, the filename is Paradox's."""
        import unicodedata
        def flat(x):
            x = unicodedata.normalize("NFKD", x.lower())
            return re.sub(r"[^a-z]", "", x)
        c, n = flat(comment), flat(name)
        if not c or not n:
            return True
        if c in n or n in c:
            return True
        for group in ALIASES:
            if any(a in c for a in group) and any(a in n for a in group):
                return True
        return False

    # `owns = 298  # Kursk`, `1945 = { ... }  # Novgorod-Seversky`, etc.
    PROV_COMMENT = re.compile(
        r"^[^#\n]*?\b(?:owns|province_id|owns_core_province|owns_or_non_sovereign_subject_of)"
        r"\s*=\s*(\d+)\s*#\s*([^\n]+)$", re.M)
    for path in script_files():
        text, _ = decode(read(path))
        for m in PROV_COMMENT.finditer(text):
            pid, comment = int(m.group(1)), m.group(2).strip()
            comment = re.split(r"\s*[-(]", comment)[0].strip()
            line = text.count("\n", 0, m.start()) + 1
            real = province_name.get(pid)
            if real is None:
                err(f"{path}:{line}: province {pid} does not exist "
                    f"(comment says '{comment}')")
            elif not looks_like(comment, real):
                err(f"{path}:{line}: province {pid} is '{real}', "
                    f"but the comment says '{comment}'")

# --- 7. province renames must land on provinces the mod is actually about --

# common/province_names/*.txt and PROVnnnn localisation keys rename provinces
# by tag or culture. Both were written assuming that consecutive ids meant
# neighbouring places, which in EU4 they do not: UZH.txt renamed provinces in
# Bohemia and Spain to Transcarpathian towns. Anything outside the regions the
# mod is set in is almost certainly that mistake.
if EU4_DIR:
    MOD_REGIONS = {
        "ruthenia_region", "crimea_region", "pontic_steppe_region",
        "poland_region", "baltic_region", "carpathia_region",
        "russia_region", "moldavia_region", "ural_region",
        "balkan_region", "hungary_region",
    }
    defn_name = {}
    for line in io.open(os.path.join(EU4_DIR, "map", "definition.csv"),
                        encoding="cp1252", errors="replace"):
        parts = line.split(";")
        if len(parts) > 4 and parts[0].isdigit():
            defn_name[int(parts[0])] = parts[4].strip()

    area_of, region_of = {}, {}
    atext = re.sub(r"#.*", "", read_text := decode(read(
        os.path.join(EU4_DIR, "map", "area.txt")))[0])
    for m in re.finditer(r"([a-z_0-9]+)\s*=\s*\{([^{}]*)\}", atext):
        for i in m.group(2).split():
            if i.isdigit():
                area_of[int(i)] = m.group(1)
    rtext = re.sub(r"#.*", "", decode(read(
        os.path.join(EU4_DIR, "map", "region.txt")))[0])
    for m in re.finditer(r"([a-z_0-9]+)\s*=\s*\{(.*?)\n\}", rtext, re.S):
        for a in re.findall(r"([a-z_0-9]+_area)", m.group(2)):
            region_of[a] = m.group(1)

    def region_for(pid):
        return region_of.get(area_of.get(pid, ""), "")

    renames = []   # (path, line, pid, newname, global_key)
    for path in glob.glob("common/province_names/*.txt"):
        path = path.replace("\\", "/")
        # A file named for a culture (ruthenian.txt) is meant to rename the
        # whole world - vanilla does the same for Russian. Only files named
        # for a tag (CHR.txt) should stay inside that tag's horizon.
        if not re.match(r"^[A-Z]{3}\.txt$", os.path.basename(path)):
            continue
        text, _ = decode(read(path))
        for m in re.finditer(r'^(\d+)\s*=\s*"([^"]*)"', text, re.M):
            renames.append((path, text.count("\n", 0, m.start()) + 1,
                            int(m.group(1)), m.group(2), False))
    for path in loc_files():
        text, _ = decode(read(path))
        for m in re.finditer(r'^\s*PROV(\d+):\s*\d*\s*"([^"]*)"', text, re.M):
            renames.append((path, text.count("\n", 0, m.start()) + 1,
                            int(m.group(1)), m.group(2), True))

    for path, line, pid, newname, is_global in renames:
        reg = region_for(pid)
        if not area_of.get(pid):
            # Sea zones legitimately get renamed ("Odesa Bay"); only a global
            # key can do that, and only a sea zone has no area.
            if not is_global:
                err(f"{path}:{line}: renames province {pid} to '{newname}', "
                    f"but {pid} is in no area")
        elif reg and reg not in MOD_REGIONS:
            # Respelling a name the mod's glossary covers ("Gulf of Odessa" ->
            # "Odesa Bay") is house style, not a misplaced province.
            if looks_like(newname, defn_name.get(pid, "")):
                continue
            msg = (f"{path}:{line}: renames province {pid} to '{newname}', but "
                   f"{pid} is {defn_name.get(pid, '?')} in {area_of[pid]} ({reg})")
            if is_global:
                err(msg + " - a global key, so every player sees this")
            else:
                warn(msg + " - far outside this tag's horizon")

# --- 8. event pictures and opinion modifiers must exist --------------------

# Both fail quietly: a bad picture renders as a blank frame, a bad opinion
# modifier just does nothing. Neither shows up without reading error.log.
if EU4_DIR:
    sprites = set()
    for d in (os.path.join(EU4_DIR, "interface"), "interface", "gfx"):
        for path in glob.glob(os.path.join(d, "**", "*.gfx"), recursive=True):
            text, _ = decode(read(path))
            sprites.update(re.findall(r'name\s*=\s*"([A-Za-z0-9_]+_eventPicture)"',
                                      text))
            sprites.update(re.findall(r'\b([A-Za-z0-9_]+_eventPicture)\b', text))
    # Vanilla itself names pictures that ship with DLC and are absent from a
    # base install - WomenInHistory alone does it a hundred times. Anything
    # vanilla references is fine for the mod to reference too; only names the
    # mod invented are worth reporting.
    for path in glob.glob(os.path.join(EU4_DIR, "events", "*.txt")):
        text, _ = decode(read(path))
        sprites.update(re.findall(r"^\s*picture\s*=\s*\"?([A-Za-z0-9_]+)\"?\s*$",
                                  uncomment(text), re.M))

    opinions = set()
    for d in (os.path.join(EU4_DIR, "common", "opinion_modifiers"),
              os.path.join("common", "opinion_modifiers")):
        for path in glob.glob(os.path.join(d, "*.txt")):
            body = strip_comments(decode(read(path))[0])
            depth = 0
            for m in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*\{|\}", body):
                if m.group(0) == "}":
                    depth -= 1
                    continue
                if depth == 0:
                    opinions.add(m.group(1))
                depth += 1

    for path in script_files():
        text, _ = decode(read(path))
        body = uncomment(text)
        for m in re.finditer(r"^\s*picture\s*=\s*\"?([A-Za-z0-9_]+)\"?\s*$",
                             body, re.M):
            if sprites and m.group(1) not in sprites:
                line = body.count("\n", 0, m.start()) + 1
                err(f"{path}:{line}: event picture '{m.group(1)}' is not "
                    f"defined in any .gfx (renders blank)")
        for m in re.finditer(
                r"(?:add_opinion|reverse_add_opinion|has_opinion_modifier|remove_opinion)"
                r"\s*=\s*\{[^{}]*?\bmodifier\s*=\s*\"?([A-Za-z0-9_]+)\"?", body):
            if opinions and m.group(1) not in opinions:
                line = body.count("\n", 0, m.start()) + 1
                err(f"{path}:{line}: opinion modifier '{m.group(1)}' is not "
                    f"defined (the effect does nothing)")

# --- report ----------------------------------------------------------------

for w in warnings:
    print("WARN  " + w)
for e in errors:
    print("ERROR " + e)

print()
print(f"{len(list(script_files()))} script files, {len(list(loc_files()))} localisation files")
print("vanilla localisation: " + (f"{len(vanilla_english)} keys from {EU4_DIR}"
                                  if EU4_DIR else "NOT FOUND - set EU4_DIR"))
print(f"{len(event_ids)} events, {len(defined_modifiers)} event modifiers")
print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
