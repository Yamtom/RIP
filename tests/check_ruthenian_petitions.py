"""Check the twelve country decisions, both ways to resolve them, and their UI."""
import re

from clausewitz_testlib import ROOT, keyed_blocks, named_block, read


def event_id(block):
    return re.search(r"\bid = (\w+\.\d+)", block)[1]


def verify_country(tag):
    filename = f"RIP_{tag}_RuthenianPetitions.txt"
    decisions = read("decisions/" + filename)
    events = [b for _, b in keyed_blocks(read("events/" + filename), "country_event")
              if re.search(r"(?m)^\ttitle = ", b)]
    by_id = {event_id(block): block for block in events}
    assert len(by_id) == len(events) == 12, filename
    names = re.findall(r"(?m)^\t(\w+) = \{", decisions)
    assert len(set(names)) == len(names) == 6
    reachable, keys = set(), set()
    for name in names:
        decision = named_block(decisions, name)
        potential = named_block(decision, "potential")
        effect = named_block(decision, "effect")
        assert f"tag = {tag}" in potential
        flag = name + "_heard"
        assert f"NOT = {{ has_country_flag = {flag} }}" in potential
        assert effect.index("set_country_flag = " + flag) < effect.index("country_event")
        first = event_id(effect)
        intro = by_id[first]
        paid, immediate = [option for _, option in keyed_blocks(intro, "option")]
        currency, amount = re.search(r"trigger = \{ (\w+) = (\d+) \}", paid).groups()
        assert f"add_{currency} = -{amount}" in paid
        followup, days = re.search(r"country_event = \{ id = (\w+\.\d+) days = (\d+) \}", paid).groups()
        assert 0 < int(days) <= 365
        assert "country_event =" not in immediate and "trigger =" not in immediate
        assert len(list(keyed_blocks(by_id[followup], "option"))) == 1
        assert first not in reachable and followup not in reachable
        reachable.update((first, followup))
        keys.update((name + "_title", name + "_desc"))
        for body in (intro, by_id[followup]):
            assert "is_triggered_only = yes" in body
            keys.update(re.findall(r"(?m)^\s*(?:title|desc|name|custom_tooltip) = (rip_\S+)", body))
    assert reachable == set(by_id)
    return keys


expected = verify_country("RUS") | verify_country("LIT")
for language in ("english", "french", "german", "spanish"):
    path = ROOT / "localisation" / f"RIP_shared_ruthenian_petitions_l_{language}.yml"
    entries = re.findall(r'^ (\S+):0 "[^"\n]+"$', path.read_text(encoding="utf-8-sig"), re.M)
    assert set(entries) == expected and len(entries) == len(expected), language
print("PASS: 12 one-shot decisions, 24 reachable events, guarded payments, immediate alternatives and four UI catalogues")
