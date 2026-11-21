"""Contracts for decision visibility, core requirements and KRU name resets."""
from itertools import combinations

from church_testlib import World, parse
from clausewitz_testlib import named_block, normalized, read


regional = read("decisions/PolesianBelarusianNations.txt")
for decision in ("polesian_nation", "polotsk_nation", "belarus_nation"):
    potential = normalized(named_block(named_block(regional, decision), "potential"))
    assert "NOT = { tag = KRU }" in potential, decision
    assert "NOT = { has_country_flag = rus_flag }" in potential, decision

paths = read("decisions/KyivTriggers.txt")
for decision in ("rus_nation", "kyiv_factional_ruthenia", "kyiv_veche_republic", "kyiv_metropolitan_theocracy"):
    effect = named_block(named_block(paths, decision), "effect")
    assert effect.index("change_tag = KRU") < effect.index("on_change_tag_effect = yes") < effect.index("rip_kru_set_realm_name = yes")


class FormationWorld(World):
    def condition(self, key, value, scope, root, prev):
        if key == "owns_core_province":
            return value in scope["cores"]
        return super().condition(key, value, scope, root, prev)


world = FormationWorld()
country = world.country("KIE")
heartland = {"280", "283"}
lands = heartland | {"261", "279", "289", "291"}
for nation, filename in (("ruthenian_nation", "RuthenianNation"), ("kuyaba_nation", "KuyabaNation")):
    allow = named_block(named_block(read(f"decisions/{filename}.txt"), nation), "allow")
    requirements = [(k, v) for k, v in parse(allow)[0][1] if k in ("if", "owns_core_province")]
    for world.year in (1774, 1775):
        for country["dip"] in (4, 5):
            needed = heartland if country["dip"] == 5 else lands
            if nation == "kuyaba_nation" and world.year >= 1775:
                needed = needed - {"291"}
            for count in range(len(lands) + 1):
                for owned in combinations(lands, count):
                    country["cores"] = set(owned)
                    assert world.gate(requirements, country) == (needed <= country["cores"]), (nation, world.year, country["dip"], owned)
print("PASS: regional formations exclude restored Rus, four naming paths follow the tag reset, 512 core scenarios.")
