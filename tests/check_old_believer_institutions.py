"""Bounded source execution, not native EU4/runtime proof.

Exercise delayed confirmations, ownership changes, conversion cleanup and
cooldown persistence. Unknown effects/triggers fail in the shared interpreter.
"""
from copy import deepcopy
import re
from church_testlib import World, EFFECTS, TRIGGERS, parse
from clausewitz_testlib import ROOT, read, named_block

EFFECTS.update(parse(read("common/scripted_effects/rip_ob_institution_effects.txt")))
TRIGGERS.update(parse(read("common/scripted_triggers/rip_ob_institution_triggers.txt")))
DECISIONS = dict(dict(parse(read("decisions/RIP_OldBelieverInstitutions.txt")))["country_decisions"])
EVENTS = {
    dict(body)["id"]: body
    for key, body in parse(read("events/RIP_OldBelieverInstitutions.txt"))
    if key == "country_event"
}


class Fixture(World):
    def condition(self, key, value, scope, root, prev):
        if key == "is_capital":
            return (self.countries[scope["owner"]]["capital"] == scope["id"]) == (value == "yes")
        if key == "has_missionary":
            return scope.get("has_missionary", False) == (value == "yes")
        return super().condition(key, value, scope, root, prev)


def fixture():
    w = Fixture()
    w.year = 1700
    c = w.country("MOS", "old_believer")
    p = w.province(295, c, "old_believer")
    minority = w.province(296, c, "orthodox")
    minority["flags"]["rip_ob_community"] = w.day
    minority["modifiers"]["rip_ob_local_community"] = float("inf")
    other = w.country("LIT", "catholic")
    return w, c, p, minority, other


def available(w, c, name):
    decision = dict(DECISIONS[name])
    return w.gate(decision["potential"], c) and w.gate(decision["allow"], c)


def open_decision(w, c, name):
    assert available(w, c, name), name
    w.execute(dict(DECISIONS[name])["effect"], c)


def option(event, name):
    return next(body for key, body in EVENTS[event] if key == "option" and dict(body)["name"] == name)


def can_choose(w, c, event, name):
    return w.gate(dict(option(event, name)).get("trigger", []), c)


def choose(w, c, event, name):
    assert can_choose(w, c, event, name), (event, name)
    w.execute([(k, v) for k, v in option(event, name) if k not in ("name", "trigger", "ai_chance")], c)


# State gate and affordability, including a queued popup after resources change.
w, c, capital, minority, other = fixture()
for change in ({"religion": "orthodox"}, {"is_at_war": True}, {"stability": -1},
               {"adm_power": 74}, {"treasury": 99}):
    before = deepcopy(c)
    c.update(change)
    assert not available(w, c, "rip_ob_choose_accord"), change
    c.clear(); c.update(before)
w.year = 1665
assert not available(w, c, "rip_ob_choose_accord")
w.year = 1666
open_decision(w, c, "rip_ob_choose_accord")
assert not available(w, c, "rip_ob_choose_accord"), "pending popup must lock its decision"
c["treasury"] = 99
assert not can_choose(w, c, "rip_ob_institutions.1", "rip_ob_institutions.1.a")
choose(w, c, "rip_ob_institutions.1", "rip_ob_institutions.defer")
assert c["adm_power"] == 500 and c["treasury"] == 99
c["treasury"] = 1000
open_decision(w, c, "rip_ob_choose_accord")
choose(w, c, "rip_ob_institutions.1", "rip_ob_institutions.1.a")
assert (c["adm_power"], c["treasury"], c["stability"]) == (425, 900, 2)
assert not can_choose(w, c, "rip_ob_institutions.1", "rip_ob_institutions.1.a"), "no replay"
assert not available(w, c, "rip_ob_choose_accord")
w.day = 7299
assert not available(w, c, "rip_ob_choose_accord")
w.day = 7300
open_decision(w, c, "rip_ob_choose_accord")
choose(w, c, "rip_ob_institutions.1", "rip_ob_institutions.1.b")
assert c["stability"] == 1 and "rip_ob_priestly_accord" not in c["modifiers"]
assert "rip_ob_lay_accord" in c["flags"] and "rip_ob_lay_accord" in c["modifiers"]

# One assembly mandate, exact cost and ten-year lock, religion-change cleanup.
open_decision(w, c, "rip_ob_hold_assembly")
choose(w, c, "rip_ob_institutions.2", "rip_ob_institutions.2.a")
assert (c["adm_power"], c["treasury"]) == (300, 725)
assert c["modifiers"]["rip_ob_manuscript_mandate"] == w.day + 3650
assert not available(w, c, "rip_ob_hold_assembly")
saved_locks = {k: v for k, v in c["flags"].items() if k.endswith(("held", "changed"))}
c["religion"] = "catholic"
w.run("rip_ob_institutions_upkeep_effect", c)
assert not any(k in c["modifiers"] for k in ("rip_ob_lay_accord", "rip_ob_manuscript_mandate"))
assert all(c["flags"][k] == v for k, v in saved_locks.items())
c["religion"] = "old_believer"
w.run("rip_ob_institutions_upkeep_effect", c)
assert "rip_ob_lay_accord" in c["modifiers"]
assert "rip_ob_manuscript_mandate" not in c["modifiers"], "no free restoration of timed mandate"
w.day += 3650
open_decision(w, c, "rip_ob_hold_assembly")
choose(w, c, "rip_ob_institutions.2", "rip_ob_institutions.2.b")
assert "rip_ob_mutual_aid_mandate" in c["modifiers"] and "rip_ob_manuscript_mandate" not in c["modifiers"]

# Refuge selection excludes capitals, occupation, absent cores and missionaries.
w, c, capital, minority, other = fixture()
assert not w.gate(TRIGGERS["rip_ob_refuge_site"], capital)
for field, invalid in (("controlled_by", "LIT"), ("core", "LIT"), ("has_missionary", True)):
    saved = minority.get(field)
    minority[field] = invalid
    assert not available(w, c, "rip_ob_endow_refuge")
    if saved is None:
        minority.pop(field)
    else:
        minority[field] = saved
open_decision(w, c, "rip_ob_endow_refuge")
assert w.targets["rip_ob_refuge_site"] is minority
assert not available(w, c, "rip_ob_endow_refuge")
minority["owner"] = other["id"]
assert not can_choose(w, c, "rip_ob_institutions.3", "rip_ob_institutions.3.a"), "recheck ownership"
choose(w, c, "rip_ob_institutions.3", "rip_ob_institutions.defer")
assert c["treasury"] == 1000 and c["dip_power"] == 500
minority["owner"] = c["id"]
open_decision(w, c, "rip_ob_endow_refuge")
choose(w, c, "rip_ob_institutions.3", "rip_ob_institutions.3.a")
assert c["treasury"] == 900 and c["dip_power"] == 450
assert minority["local_autonomy"] == 10 and minority["religion"] == "orthodox", "minority is not converted"
assert "rip_ob_refuge_founded" in minority["flags"] and "rip_ob_active_refuge" in minority["modifiers"]
assert not available(w, c, "rip_ob_endow_refuge")
minority["owner"] = other["id"]
w.run("rip_ob_refresh_refuge_effect", minority)
assert "rip_ob_active_refuge" not in minority["modifiers"]
assert "rip_ob_inactive_refuge" in minority["modifiers"], "visible suspended foundation"
assert {"rip_ob_community", "rip_ob_refuge_founded"} <= set(minority["flags"])
other["flags"]["rip_ob_toleration"] = w.day
w.run("rip_ob_refresh_refuge_effect", minority)
assert "rip_ob_active_refuge" in minority["modifiers"]
assert "rip_ob_inactive_refuge" not in minority["modifiers"]
other["flags"]["rip_ob_repression"] = w.day
w.run("rip_ob_refresh_refuge_effect", minority)
assert "rip_ob_active_refuge" not in minority["modifiers"], "repression overrides protection"
w.run("rip_ob_tolerate_effect", other)
assert "rip_ob_active_refuge" in minority["modifiers"], "toleration reactivates immediately"
w.run("rip_ob_repress_effect", other)
assert "rip_ob_active_refuge" not in minority["modifiers"], "repression suspends immediately"
# Three owned foundations close new funding, even after cooldown.
minority["owner"] = c["id"]
for number in (297, 298):
    p = w.province(number, c, "old_believer")
    p["flags"]["rip_ob_refuge_founded"] = w.day
w.province(299, c, "old_believer")
w.day += 3650
assert not available(w, c, "rip_ob_endow_refuge"), "foundation cap"

# No native patriarchate, no unguarded event effects in else branches, exact wiring.
religion = named_block(read("common/religions/zzz_old_believer.txt"), "old_believer")
assert "has_patriarchs = yes" not in religion
adoption = named_block(read("decisions/RIP_OldBelievers.txt"), "rip_ob_adopt_old_rite")
assert adoption.index("rip_ob_leave_patriarchate_effect = yes") < adoption.index("change_religion = old_believer")
rebels = named_block(read("common/rebel_types/old_believer.txt"), "demands_enforced_effect")
assert rebels.index("rip_ob_leave_patriarchate_effect = yes") < rebels.index("change_religion = old_believer")
w, c, _, _, _ = fixture()
c["religion"] = "orthodox"
c["patriarch_authority"] = 0.85
w.run("rip_ob_leave_patriarchate_effect", c)
assert c["patriarch_authority"] <= 0, "relinquish authority before disabling its native mechanic"
hooks = read("common/on_actions/RIP_religion_old_believer_on_actions.txt")
for name in ("on_startup", "on_yearly_pulse", "on_religion_change"):
    assert "rip_ob_institutions_upkeep_effect = yes" in named_block(hooks, name)
assert "rip_ob_refresh_refuge_effect = yes" in named_block(hooks, "on_province_owner_change")
events_text = read("events/RIP_OldBelieverInstitutions.txt")
assert events_text.count("is_triggered_only = yes") == 3
assert not re.search(r"\belse(?:_if)?\s*=", events_text)
for lang in ("english", "french", "german", "spanish"):
    path = ROOT / f"localisation/replace/zzzz_RIP_church_redesign_l_{lang}.yml"
    raw = path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf") and not raw[3:].startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    for key in ("rip_ob_choose_accord_title", "rip_ob_hold_assembly_title", "rip_ob_endow_refuge_title",
                "rip_ob_institutions.3.d", "desc_rip_ob_active_refuge"):
        assert len(re.findall(rf"(?m)^ {re.escape(key)}:", text)) == 1, (lang, key)
for _, body in parse(read("customizable_localization/rip_old_believer_institutions.txt")):
    assert dict(body)["random"] == "no", "first matching display state, never a random fallback"
# Modifier keys must be documented by the installed target game's own sample.
from clausewitz_testlib import vanilla_root
vanilla = vanilla_root()
if vanilla:
    sample = (vanilla / "common/event_modifiers/02_test_modifiers.txt").read_text(encoding="utf-8-sig")
    native_keys = set(re.findall(r"\b([A-Za-z0-9_]+)\s*=", sample))
    for modifier, body in parse(read("common/event_modifiers/rip_ob_institution_modifiers.txt")):
        for key, _ in body:
            assert key in native_keys, (modifier, key, "absent from native modifier documentation")
print("PASS: Old Believer institutions; confirmations, payments, locks, conversion, conquest, minority continuity and wiring (source model only)")
