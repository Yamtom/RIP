"""Static VFS, reachability, tier, and narrative contracts for RIP reforms."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read, vanilla_root


REFORMS_DIR = ROOT / "common/government_reforms"
EXPECTED_REFORM_COUNT = 124
EXPECTED_REFORM_ID_SHA256 = "413794df333eaae69b8c96c488f02de3d14fd5157d453d140f2761f729917e88"
ROLE_ONLY_REFORMS = (
    "kyivan_veche_reform",
    "kyivan_boyar_republic_reform",
    "kyivan_metropolitanate_reform",
    "kyivan_church_synod_reform",
    "hlc_boyar_republic_reform",
    "hlc_boyar_oligarchy_reform",
    "hlc_halych_metropolitanate_reform",
    "hlc_halych_synodal_confirmation_reform",
    "hlc_lviv_uniate_synod_reform",
    "vln_sejmik_republic_reform",
    "vln_dietine_instructions_reform",
    "uzh_mukachevo_eparchy_reform",
    "uzh_uzhhorod_seat_translation_reform",
    "uzh_presov_eparchy_reform",
)
VANILLA_OVERRIDE_REFORMS = {
    "principality",
    "tsardom",
    "great_veche_republic",
    "lands_for_the_monasteries_reform",
    "holy_synod_reform",
    "strengthened_the_patriarchy_reform",
    "head_of_the_patriarchy_reform",
    "orthodox_patriarchate_reform",
}


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def exclusive_entry_sets(government: str) -> list[set[str]]:
    return [
        set(re.findall(r"\b[a-z][a-z0-9_]*\b", re.sub(r"#.*", "", block)))
        for _, block in keyed_blocks(government, "exclusive_reforms")
    ]


def reform_sources() -> tuple[str, dict[str, Path]]:
    chunks: list[str] = []
    owners: dict[str, Path] = {}
    for path in sorted(REFORMS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        chunks.append(text)
        for reform in re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text):
            if reform in owners:
                raise ValueError(
                    f"duplicate reform {reform}: {owners[reform].name}, {path.name}"
                )
            owners[reform] = path
    return "\n".join(chunks), owners


def check_vfs_and_schema(failures: list[str], reforms: str, owners: dict[str, Path]) -> None:
    require(
        failures,
        not (REFORMS_DIR / "RIP_government_reforms.txt").exists(),
        "obsolete monolithic reform file still exists",
    )
    require(
        failures,
        len(owners) == EXPECTED_REFORM_COUNT,
        f"expected {EXPECTED_REFORM_COUNT} unique reforms, found {len(owners)}",
    )
    reform_id_hash = hashlib.sha256("\n".join(sorted(owners)).encode("utf-8")).hexdigest()
    require(
        failures,
        reform_id_hash == EXPECTED_REFORM_ID_SHA256,
        "government reform ID set changed (possible deleted/renamed save key)",
    )
    reform_map = read("docs/GOVERNMENT_REFORMS_MAP.uk.md")
    for reform in owners:
        require(
            failures,
            f"`{reform}`" in reform_map,
            f"government reform is missing from the visual map: {reform}",
        )
    require(
        failures,
        f"{EXPECTED_REFORM_COUNT} унікальних definition-ID" in reform_map,
        "visual map reports a stale government reform count",
    )
    authenticity_doc = read("docs/GOVERNMENT_AUTHENTICITY_105.uk.md")
    documented_authenticity_ids = set(
        re.findall(r"(?m)^\| `([A-Za-z0-9_]+)`", authenticity_doc)
    )
    require(
        failures,
        documented_authenticity_ids == set(owners),
        "government authenticity document does not cover exactly the live reform definitions",
    )
    require(
        failures,
        f"ця таблиця охоплює всі **{EXPECTED_REFORM_COUNT} визначення реформ**"
        in normalized(authenticity_doc),
        "government authenticity document reports a stale total reform count",
    )
    for reform in ROLE_ONLY_REFORMS:
        row = next(
            (
                line
                for line in authenticity_doc.splitlines()
                if line.startswith(f"| `{reform}`")
            ),
            "",
        )
        require(
            failures,
            bool(row) and "кампанійн" in row and "сертифік" in row,
            f"{reform} lacks an explicit no-campaign-certification note in the authenticity document",
        )
    for path in sorted(REFORMS_DIR.glob("*.txt")):
        require(failures, not path.read_bytes().startswith(b"\xef\xbb\xbf"), f"BOM: {path.name}")

    for stale in (
        "max_states",
        "monarch_mil_power",
        "prussian_republic_legacy",
        "monastic_order_legacy",
        'icon = "merchant_republic"',
        'icon = "monastic_order"',
    ):
        require(failures, stale not in reforms, f"stale or invalid reform token remains: {stale}")


def check_registration(failures: list[str], owners: dict[str, Path]) -> None:
    governments = read("common/governments/00_governments.txt")
    registered_chunks: list[str] = []
    for government_type in ("monarchy", "republic", "tribal", "native", "theocracy"):
        government = named_block(governments, government_type)
        basic_match = re.search(r"(?m)^\s*basic_reform\s*=\s*([A-Za-z0-9_]+)", government)
        if basic_match:
            registered_chunks.append(basic_match.group(1))
        reform_levels = named_block(government, "reform_levels")
        registered_chunks.extend(block for _, block in keyed_blocks(reform_levels, "reforms"))
    registered = normalized("\n".join(registered_chunks))
    for reform in owners:
        require(
            failures,
            re.search(rf"\b{re.escape(reform)}\b", registered) is not None,
            f"unregistered reform: {reform}",
        )

    m4 = normalized(named_block(governments, "state_and_religion"))
    m6 = normalized(named_block(governments, "deliberative_assembly"))
    m7 = normalized(named_block(governments, "growth_of_administration"))
    m8 = normalized(named_block(governments, "economical_matters"))
    m11 = normalized(named_block(governments, "separation_of_power"))
    r8 = normalized(named_block(governments, "economical_matters_republic"))
    require(failures, "assembly_houses_reform" in m6, "Assembly Houses is not registered at M6")
    for reform in (
        "sacred_regulation_reform",
        "patriarch_engagement_reform",
        "uzh_union_synod_reform",
    ):
        require(failures, reform in m4, f"religious reform is not registered at M4: {reform}")
    for reform in ("vln_magdeburg_rights", "chr_grain_directorate_reform"):
        require(failures, reform in m8, f"economic reform is not registered at M8: {reform}")
    for reform in ("merchant_nobility_reform", "open_trading_ports_reform"):
        require(
            failures,
            reform in m8,
            f"commercial Ruthenian reform is not registered at M8: {reform}",
        )
        require(
            failures,
            reform not in m7,
            f"commercial Ruthenian reform remains registered at M7: {reform}",
        )
    for reform in ("chr_grain_directorate_reform", "zaz_chaiky_trade_reform"):
        require(failures, reform in r8, f"economic reform is not registered at R8: {reform}")
    republic_levels = normalized(
        named_block(named_block(governments, "republic"), "reform_levels")
    )
    for reform in (
        "pdl_enlightened_voivodeship_reform",
        "pdl_revolutionary_republic_reform",
    ):
        require(
            failures,
            reform in m11 and reform not in m7 and reform not in republic_levels,
            f"late Podillian monarchical settlement is not aligned with vanilla M11: {reform}",
        )

    # One parliament per monarchy, as in vanilla (parliamentary_reform against the
    # tier-1 parliaments such as polish_great_sejm). The Union of Two Nations has
    # "one diet" and the Diet of the Grand Duchy "sits apart from the Crown's
    # Sejm"; holding both made two. The scripted union path removes the Diet
    # first, so the result does not depend on how the engine treats a scripted
    # add_government_reform against exclusive_reforms.
    parliament_sets = [
        normalized(block)
        for _, block in keyed_blocks(
            named_block(governments, "monarchy"), "exclusive_reforms"
        )
        if "assembly_houses_reform" in normalized(block)
    ]
    require(
        failures,
        len(parliament_sets) == 1
        and all(
            re.search(rf"\b{reform}\b", parliament_sets[0])
            for reform in (
                "parliamentary_reform",
                "polish_great_sejm",
                "assembly_houses_reform",
                "lit_grand_diet_reform",
                "lit_union_of_two_nations_reform",
            )
        ),
        "Union of Two Nations and the Diet of the Grand Duchy are not exclusive with the vanilla parliaments",
    )
    union_decision = normalized(
        named_block(read("decisions/UnionDispute.txt"), "lit_hold_the_union_on_our_terms")
    )
    drop_diet = "remove_government_reform = lit_grand_diet_reform"
    add_union = "add_government_reform = lit_union_of_two_nations_reform"
    require(
        failures,
        drop_diet in union_decision
        and add_union in union_decision
        and union_decision.index(drop_diet) < union_decision.index(add_union),
        "the union decision does not drop the Grand Duchy's diet before it adds the Commonwealth's",
    )

    m1 = normalized(named_block(governments, "feudalism_vs_autocracy"))
    m2 = normalized(named_block(governments, "hereditary_vs_nobility"))
    m10 = normalized(named_block(governments, "absolute_rule_vs_constitutional"))
    for pair, tier in (
        (("hlc_magnate_assembly_reform", "hlc_centralized_voivodeship_reform"), m2),
        (("hlc_galician_sejm_reform", "hlc_austrian_bureaucracy_reform"), m6),
        (("hlc_crown_authority_reform", "hlc_crown_and_sejm_reform"), m10),
    ):
        require(failures, all(item in tier for item in pair), f"HLC alternatives do not share a tier: {pair}")

    r1 = normalized(named_block(governments, "oligarchy_merchant_class_noble_elite"))
    r10 = normalized(named_block(governments, "guiding_principle_of_administration"))
    require(
        failures,
        "uzh_palanok_captaincy_reform" in m1
        and "uzh_palanok_captaincy_reform" in r1,
        "UZH Palanok Captaincy lacks its M1/R1 start tiers",
    )
    require(
        failures,
        "uzh_komitat_system_reform" in m1
        and "uzh_komitat_system_reform" not in r1
        and "uzh_republican_komitat_system_reform" in r1
        and "uzh_republican_komitat_system_reform" not in m1,
        "UZH Komitat variants are not separated into M1 and R1",
    )
    for reform in (
        "uzh_palatial_ruthenian_reform",
        "uzh_palatial_rusyn_reform",
    ):
        require(failures, reform in m10 and reform in r10, f"UZH Palatial reform lacks an M10/R10 tier: {reform}")
    uzh_palatial = named_block(
        read("common/government_reforms/RIP_UZH_government_reforms.txt"),
        "uzh_palatial_ruthenian_reform",
    )
    uzh_modifiers = named_block(uzh_palatial, "modifiers")
    uzh_conditionals = [block for _, block in keyed_blocks(uzh_palatial, "conditional")]
    gated_conditional = uzh_conditionals[0] if len(uzh_conditionals) == 1 else ""
    conditional_allow = named_block(gated_conditional, "allow") if gated_conditional else ""
    dlc_ors = [block for _, block in keyed_blocks(conditional_allow, "OR")]
    dlc_gate = dlc_ors[0] if len(dlc_ors) == 1 else ""
    dlc_names = re.findall(r'(?m)^\s*has_dlc\s*=\s*"([^"]+)"\s*$', dlc_gate)
    require(
        failures,
        "parliament_backing_chance" not in uzh_modifiers
        and len(uzh_conditionals) == 1
        and len(dlc_ors) == 1
        and len(dlc_names) == 2
        and set(dlc_names) == {"Common Sense", "Domination"}
        and "has_parliament = yes" in normalized(gated_conditional)
        and "parliament_backing_chance = 0.1" in normalized(gated_conditional)
        and "blocked_call_diet = yes" in normalized(gated_conditional),
        "UZH Palatial parliament modifiers are not confined to the single DLC-gated conditional",
    )
    require(
        failures,
        "uzh_palatial_uhro_reform" in m10
        and "uzh_palatial_uhro_reform" not in r10
        and "uzh_palatial_uhro_republic_reform" in r10
        and "uzh_palatial_uhro_republic_reform" not in m10,
        "UZH Ugro-Rusyn Palatial variants are not separated into M10 and R10",
    )

    monarchy = named_block(governments, "monarchy")
    republic = named_block(governments, "republic")
    monarchy_groups = exclusive_entry_sets(monarchy)
    republic_groups = exclusive_entry_sets(republic)
    special_m1_monarchies = (
        "ruthenian_factional_empire_reform",
        "ruthenian_factional_empire_princes_hetmans_reform",
        "ruthenian_factional_empire_boyars_hetmans_reform",
        "uzh_palanok_captaincy_reform",
        "lit_union_of_two_nations_reform",
    )
    kyivan_states_general_monarchies = (
        "kyivan_rus_reform",
        "kyivan_shogunate_reform",
    )
    states_general_group = (
        "states_general_reform",
        *special_m1_monarchies,
        *kyivan_states_general_monarchies,
    )
    require(
        failures,
        any(set(states_general_group) <= group for group in monarchy_groups),
        "M1 factional, Kyivan, Palanok, and Union monarchies are not exclusive with vanilla States General",
    )
    monarchy_parliament_group = (
        "parliamentary_reform",
        "assembly_houses_reform",
        *special_m1_monarchies,
        "chr_many_nations_union_reform",
        "representation_monarchy_reform",
        "hlc_crown_and_sejm_reform",
        "vln_grand_ruthenia_reform",
        "uzh_palatial_ruthenian_reform",
        "legislative_rada_reform",
    )
    monarchy_parliament_matches = [
        group for group in monarchy_groups if set(monarchy_parliament_group) <= group
    ]
    require(
        failures,
        bool(monarchy_parliament_matches),
        "custom M1/M10/M11 monarch assemblies can still stack with generic parliamentary reforms",
    )
    require(
        failures,
        all(
            set(kyivan_states_general_monarchies).isdisjoint(group)
            for group in monarchy_parliament_matches
        ),
        "Kyivan States General exclusivity leaked into the monarchy parliament group",
    )
    republic_parliament_group = (
        "parliamentary_reform",
        "zaz_general_rada_reform",
        "zaz_cossack_cantons_reform",
        "uzh_palatial_ruthenian_reform",
        "siversk_veche_reform",
        "chr_desna_staple_reform",
        "chr_town_union_reform",
        "chr_rada_of_lands_reform",
        "kyivan_veche_reform",
        "uzh_palanok_captaincy_reform",
    )
    require(
        failures,
        any(set(republic_parliament_group) <= group for group in republic_groups),
        "R1 Ruthenian assemblies can still stack with R6/R10 parliamentary systems",
    )
    custom_exclusive_reforms = (
        set(special_m1_monarchies)
        | set(kyivan_states_general_monarchies)
        | {
            "chr_many_nations_union_reform",
            "zaz_cossack_cantons_reform",
            "hlc_crown_and_sejm_reform",
            "representation_monarchy_reform",
            "vln_grand_ruthenia_reform",
            "uzh_palatial_ruthenian_reform",
            "legislative_rada_reform",
            "zaz_general_rada_reform",
            "siversk_veche_reform",
            "chr_desna_staple_reform",
            "chr_town_union_reform",
            "chr_rada_of_lands_reform",
            "kyivan_veche_reform",
        }
    )
    for reform in custom_exclusive_reforms:
        require(
            failures,
            reform in owners,
            f"exclusive-reform group references an undefined custom reform: {reform}",
        )

    def custom_reforms_in_levels(government: str) -> set[str]:
        reform_levels = re.sub(r"#.*", "", named_block(government, "reform_levels"))
        return set(re.findall(r"\b[a-z][a-z0-9_]*\b", reform_levels)) & set(owners)

    monarchical_only_reforms = (
        custom_reforms_in_levels(monarchy) - custom_reforms_in_levels(republic)
    )
    expected_monarchical_only_reforms = {
        "kyivan_rus_reform",
        "kyivan_shogunate_reform",
        "chr_many_nations_union_reform",
    }
    require(
        failures,
        expected_monarchical_only_reforms <= monarchical_only_reforms,
        "Kyivan national forms and the CHR union must remain monarchy-only",
    )
    republic_exclusive_text = "\n".join(
        block for _, block in keyed_blocks(republic, "exclusive_reforms")
    )
    republic_exclusive_reforms = set(
        re.findall(
            r"\b[a-z][a-z0-9_]*\b",
            re.sub(r"#.*", "", republic_exclusive_text),
        )
    )
    misplaced_monarchies = monarchical_only_reforms & republic_exclusive_reforms
    require(
        failures,
        not misplaced_monarchies,
        f"monarchy-only custom reforms remain in republic exclusive_reforms: "
        f"{sorted(misplaced_monarchies)}",
    )

    for government_type, government in (
        ("monarchy", monarchy),
        ("republic", republic),
    ):
        reform_levels = named_block(government, "reform_levels")
        registered_text = re.sub(r"#.*", "", reform_levels)
        registered_ids = set(re.findall(r"\b[a-z][a-z0-9_]*\b", registered_text))
        exclusive_text = re.sub(
            r"#.*",
            "",
            "\n".join(
                block for _, block in keyed_blocks(government, "exclusive_reforms")
            ),
        )
        listed_custom = set(re.findall(r"\b[a-z][a-z0-9_]*\b", exclusive_text)) & set(owners)
        require(
            failures,
            listed_custom <= registered_ids,
            f"unregistered custom reform in {government_type} exclusive_reforms: "
            f"{sorted(listed_custom - registered_ids)}",
        )

    installed = vanilla_root()
    if installed is not None:
        vanilla_governments = (
            installed / "common/governments/00_governments.txt"
        ).read_text(encoding="utf-8-sig")
        for government_type in ("monarchy", "republic"):
            vanilla_groups = exclusive_entry_sets(
                named_block(vanilla_governments, government_type)
            )
            current_groups = exclusive_entry_sets(
                named_block(governments, government_type)
            )
            for index, vanilla_group in enumerate(vanilla_groups, 1):
                require(
                    failures,
                    any(vanilla_group <= current_group for current_group in current_groups),
                    f"{government_type} lost or split vanilla exclusive_reforms group {index}",
                )


def check_localisation(failures: list[str], owners: dict[str, Path]) -> None:
    keys: Counter[str] = Counter()
    for path in (ROOT / "localisation").rglob("*_l_english.yml"):
        text = path.read_text(encoding="utf-8-sig")
        keys.update(re.findall(r'(?m)^\s*([A-Za-z0-9_.-]+):\d+\s+"', text))

    for reform in owners:
        for key in (reform, f"{reform}_desc"):
            if reform == "grand_duchy_reform":
                require(
                    failures,
                    keys[key] <= 1,
                    f"duplicate mod localisation for vanilla-resolved key: {key}",
                )
            else:
                require(
                    failures,
                    keys[key] == 1,
                    f"government reform localisation count is {keys[key]}, expected 1: {key}",
                )

    # GAME_DESIGN_DOCUMENT 1.3: the speculative Kyivan branches (Seniorate,
    # Cesarstvo) are labelled "Speculative Alternate History" in the tooltip, both
    # where the decision offers them and where the reform is held.
    english = read("localisation/RIP_l_english.yml")
    for key in (
        "kyiv_shogunate_path_desc",
        "kyiv_cesarstvo_path_desc",
        "kyivan_shogunate_reform_desc",
        "kyivan_cesarstvo_reform_desc",
    ):
        entry = re.search(rf'(?m)^\s*{key}:\d+\s+"(.*)"\s*$', english)
        require(
            failures,
            entry is not None and "Speculative Alternate History" in entry.group(1),
            f"speculative Kyivan branch lacks its Speculative Alternate History label: {key}",
        )


def check_reachability_and_scope(failures: list[str], reforms: str) -> None:
    ruthenian_gate = normalized(
        named_block(
            read("common/scripted_triggers/kru_ruthenian_reform_triggers.txt"),
            "ruthenian_reform_eligible",
        )
    )
    primary_cultures = re.findall(
        r"\bprimary_culture\s*=\s*([A-Za-z0-9_]+)", ruthenian_gate
    )
    expected_primary_cultures = (
        "ruthenian",
        "rusyn",
        "ruthenian_new",
        "rusyn_new",
        "rusyn_new_new",
    )
    require(
        failures,
        tuple(primary_cultures) == expected_primary_cultures
        and "accepted_culture" not in ruthenian_gate
        and "dominant_culture" not in ruthenian_gate,
        "Ruthenian reforms must require a primary Ruthenian/Rusyn culture, not acceptance or dominance",
    )
    holder_reforms = re.findall(r"\bhas_reform\s*=\s*([A-Za-z0-9_]+)", ruthenian_gate)
    expected_holder_reforms = (
        "ruthenian_principality_reform",
        "kyivan_rus_reform",
        "principality_appanage",
    )
    require(
        failures,
        tuple(holder_reforms) == expected_holder_reforms,
        "existing holders must retain Ruthenian reform visibility",
    )

    def visible(primary_culture: str, accepted=(), dominant=None, held=()) -> bool:
        # The parsed source contract is exactly primary culture OR existing
        # holder; accepted and dominant culture do not participate.
        return primary_culture in primary_cultures or any(
            reform in holder_reforms for reform in held
        )

    for culture in expected_primary_cultures:
        require(
            failures,
            visible(culture),
            f"primary Ruthenian/Rusyn culture lost reform visibility: {culture}",
        )
    require(
        failures,
        not visible("russian", accepted=("ruthenian",)),
        "an accepted Ruthenian culture alone must not show the reform family",
    )
    require(
        failures,
        not visible("russian", dominant="rusyn"),
        "a dominant Ruthenian/Rusyn culture alone must not show the reform family",
    )
    for reform in expected_holder_reforms:
        require(
            failures,
            visible("russian", held=(reform,)),
            f"an existing holder lost reform visibility: {reform}",
        )

    odesa = normalized(named_block(reforms, "odesa_trade_republic_reform"))
    require(
        failures,
        "trade_city_reform = trading_city" in odesa
        and "trading_city_legacy" not in odesa,
        "ODS modern reform still creates a legacy-system trading city",
    )

    principality = normalized(named_block(reforms, "ruthenian_principality_reform"))
    require(
        failures,
        re.search(r"\bmin_autonomy\s*=", principality) is None
        and "liberty_desire_from_subject_development = -0.15" in principality,
        "Ruthenian Principality remains an early autonomy trap instead of a subject polity",
    )
    assemblies = normalized(named_block(reforms, "elected_assemblies_reform"))
    for stale_bonus in (
        "diplomats",
        "diplomatic_reputation",
        "envoy_travel_time",
        "inflation_reduction",
    ):
        require(
            failures,
            re.search(rf"\b{stale_bonus}\s*=", assemblies) is None,
            f"Veche Assemblies still carries an unrelated stacked bonus: {stale_bonus}",
        )
    require(
        failures,
        "max_absolutism = -10" in assemblies,
        "Veche Assemblies lacks its decentralization trade-off",
    )

    patriarchal_faiths = ("orthodox", "russian_orthodox", "greek_catholic")
    for reform_id in (
        "sacred_regulation_reform",
        "patriarch_engagement_reform",
        "prl_episcopal_authority_reform",
    ):
        reform = normalized(named_block(reforms, reform_id))
        require(
            failures,
            all(f"religion = {faith}" in reform for faith in patriarchal_faiths),
            f"patriarch-authority reform is selectable outside its three Eastern-rite faiths: {reform_id}",
        )
        require(
            failures,
            "yearly_patriarch_authority = 0.005" in reform
            and "yearly_patriarch_authority = 0.002" not in reform,
            f"patriarch-authority reform does not grant standard 0.005 yearly Patriarch Authority: {reform_id}",
        )

    lit_confessional_raw = named_block(reforms, "lit_confessional_guarantee_reform")
    lit_confessional_potential = normalized(named_block(lit_confessional_raw, "potential"))
    lit_confessional_trigger = normalized(named_block(lit_confessional_raw, "trigger"))
    require(
        failures,
        lit_confessional_potential.startswith("potential = { religion = catholic")
        and lit_confessional_trigger.startswith("trigger = { religion = catholic"),
        "lit_confessional_guarantee_reform must require Catholicism at top-level of potential and trigger so converting removes the reform",
    )

    hlc_metro_decisions = read("decisions/HLCMetropolitanatePaths.txt")
    for decision_id, flag, reform_id in (
        (
            "hlc_confirm_the_metropolitan_see",
            "rip_galicia_metropolitanate_confirmed",
            "hlc_halych_synodal_confirmation_reform",
        ),
        (
            "hlc_complete_the_union_of_lviv",
            "rip_galicia_lviv_union_synod",
            "hlc_lviv_uniate_synod_reform",
        ),
    ):
        decision_block = named_block(hlc_metro_decisions, decision_id)
        potential = normalized(named_block(decision_block, "potential"))
        effect = normalized(named_block(decision_block, "effect"))
        flag_pos = effect.find(f"set_country_flag = {flag}")
        reform_pos = effect.find(f"add_government_reform = {reform_id}")
        require(
            failures,
            "west_ukraine_hlc_origin_country = yes" in potential
            and "tag = HLC" not in potential
            and flag_pos >= 0
            and reform_pos >= 0
            and flag_pos < reform_pos,
            f"HLC metropolitanate decision blocks VOL/UKR descendants or fails to enact its reform: {decision_id}",
        )

    hlc_rep_decisions = read("decisions/HLCRepublicPaths.txt")
    for decision_id in ("hlc_the_boyars_take_power", "hlc_elevate_the_metropolitan"):
        potential = normalized(
            named_block(named_block(hlc_rep_decisions, decision_id), "potential")
        )
        require(
            failures,
            "west_ukraine_hlc_origin_country = yes" in potential
            and "tag = HLC" not in potential,
            f"HLC republic/theocracy path decision blocks VOL/UKR descendants: {decision_id}",
        )

    vln_rep_decisions = read("decisions/VLNRepublicPaths.txt")
    vln_sejmik_potential = normalized(
        named_block(named_block(vln_rep_decisions, "vln_the_sejmik_asserts_itself"), "potential")
    )
    require(
        failures,
        "west_ukraine_vln_origin_country = yes" in vln_sejmik_potential
        and "tag = VLN" not in vln_sejmik_potential,
        "VLN sejmik republic decision blocks VOL/UKR descendants",
    )

    for r1_republic_id in ("hlc_boyar_republic_reform", "vln_sejmik_republic_reform"):
        r1_republic = normalized(named_block(reforms, r1_republic_id))
        require(
            failures,
            all(
                token in r1_republic
                for token in (
                    "republic = yes",
                    "republican_name = yes",
                    "royal_marriage = no",
                    "has_term_election = yes",
                )
            ),
            f"R1 republic reform lacks explicit republican flags: {r1_republic_id}",
        )

    vln_voivodeship = normalized(named_block(reforms, "vln_voivodeship_reform"))
    volhynian_host = normalized(named_block(reforms, "vln_cossack_host_reform"))
    require(
        failures,
        "allow = { NOT = { has_reform = vln_cossack_host_reform } } government_abilities = { vln_magnate_senate_mechanic }"
        in vln_voivodeship,
        "vln_voivodeship_reform does not gate vln_magnate_senate_mechanic in a conditional against vln_cossack_host_reform",
    )
    for senate_modifier in (
        "vln_senate_convened",
        "vln_magnate_house_bought",
        "vln_magnate_banners_mustered",
    ):
        require(
            failures,
            f"remove_country_modifier = {senate_modifier}" in vln_voivodeship
            and f"remove_country_modifier = {senate_modifier}" in volhynian_host,
            f"Senate modifier is not cleared upon reform change / Cossack Host adoption: {senate_modifier}",
        )
    for foreign_mechanic in (
        "militarization_mechanic",
        "monthly_militarized_society",
        "mil_tech_cost_modifier",
    ):
        require(
            failures,
            foreign_mechanic not in volhynian_host,
            f"Volhynian Host still stacks a foreign/extra military mechanic: {foreign_mechanic}",
        )
    require(
        failures,
        "cossacks_mechanic" in volhynian_host and "max_absolutism = -10" in volhynian_host,
        "Volhynian Host lost its coherent Cossack mechanic or privilege trade-off",
    )

    siversk_patrimony_file = normalized(read("common/government_mechanics/rip_siversk_patrimony.txt"))
    for sprite in (
        "GFX_rip_siversk_charter",
        "GFX_rip_siversk_towns",
        "GFX_rip_siversk_retinue",
    ):
        require(
            failures,
            sprite in siversk_patrimony_file,
            f"Siversk Patrimony does not use bespoke sprite: {sprite}",
        )
    require(
        failures,
        "has_country_modifier = rip_siversk_town_compact" in siversk_patrimony_file
        and "has_country_modifier = rip_siversk_retinue_muster" in siversk_patrimony_file
        and "has_country_modifier = rip_siversk_patrimonial_compact" in siversk_patrimony_file,
        "Siversk Patrimony interactions lack mechanical cross-synergy triggers",
    )
    chr_siversk_principality = normalized(named_block(reforms, "chr_siversk_principality_reform"))
    for compact_modifier in (
        "rip_siversk_patrimonial_compact",
        "rip_siversk_town_compact",
        "rip_siversk_retinue_muster",
    ):
        require(
            failures,
            f"remove_country_modifier = {compact_modifier}" in chr_siversk_principality,
            f"chr_siversk_principality_reform removed_effect does not clear {compact_modifier}",
        )

    last_sich = normalized(named_block(reforms, "zaz_last_sich_reform"))
    require(
        failures,
        "zaz_lineage_country = yes" in last_sich
        and "is_subject = yes" in last_sich
        and "mercs_do_not_cost_army_professionalism" not in last_sich,
        "Last Sich lacks its bounded ZAZ-lineage path or still carries the UZH-only Hungarian attribute",
    )
    for borrowed in ("jacobins_influence", "royalists_influence", "girondists_influence"):
        require(failures, borrowed not in last_sich, f"Last Sich still borrows French faction: {borrowed}")

    shared = read("common/government_reforms/RIP_shared_ruthenian_government_reforms.txt")
    volhynian = read("common/government_reforms/RIP_VLN_government_reforms.txt")
    for regional in ("vln_magdeburg_rights", "vln_ruthenian_renaissance_reform"):
        require(failures, regional in shared and regional not in volhynian, f"regional reform is still country-locked: {regional}")

    kie = read("common/government_reforms/RIP_KIE_KRU_government_reforms.txt")
    require(failures, "cossacks_mechanic" not in kie, "medieval KIE/KRU forms still expose Cossack UI")
    cesarstvo = normalized(named_block(kie, "kyivan_cesarstvo_reform"))
    hungarian_attributes = (
        "seizing_land_no_rebels_from_estate_nobles",
        "monarch_power_on_institutions",
        "mercs_do_not_cost_army_professionalism",
        "army_tradition_on_stackwipe",
    )
    for borrowed_attr in hungarian_attributes:
        require(
            failures,
            borrowed_attr not in cesarstvo,
            f"kyivan_cesarstvo_reform still stacks borrowed UZH attribute: {borrowed_attr}",
        )
    vln_grand_ruthenia = normalized(
        named_block(
            read("common/government_reforms/RIP_VLN_government_reforms.txt"),
            "vln_grand_ruthenia_reform",
        )
    )
    for borrowed_attr in hungarian_attributes:
        require(
            failures,
            borrowed_attr not in vln_grand_ruthenia,
            f"vln_grand_ruthenia_reform still carries UZH-only Hungarian attribute: {borrowed_attr}",
        )
    uzh_hungarian_roads = read("common/government_reforms/RIP_UZH_government_reforms.txt")
    for uzh_reform in (
        "uzh_palatial_uhro_reform",
        "uzh_palatial_uhro_republic_reform",
    ):
        attributes = normalized(
            named_block(named_block(uzh_hungarian_roads, uzh_reform), "custom_attributes")
        )
        require(
            failures,
            all(f"{attribute} = yes" in attributes for attribute in hungarian_attributes),
            f"{uzh_reform} no longer owns the complete UZH Uhro-Rusyn Hungarian attribute set",
        )
    uzh_attribute_owners = {
        "uzh_palatial_uhro_reform",
        "uzh_palatial_uhro_republic_reform",
    }
    for source_path in sorted(REFORMS_DIR.glob("*.txt")):
        source = source_path.read_text(encoding="utf-8-sig")
        for reform_id in re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", source):
            if reform_id in uzh_attribute_owners:
                continue
            reform_block = normalized(named_block(source, reform_id))
            for attribute in hungarian_attributes:
                require(
                    failures,
                    attribute not in reform_block,
                    f"{reform_id} duplicates UZH-only Hungarian attribute: {attribute}",
                )

    boyar_council_raw = read("common/government_mechanics/rip_hlc_boyar_council.txt")
    boyar_council = normalized(boyar_council_raw)
    boyar_confirm = normalized(named_block(boyar_council_raw, "hlc_confirm_the_boyars_in_office"))
    boyars_confirmed_mod = normalized(
        named_block(read("common/event_modifiers/west_ukraine_modifiers.txt"), "hlc_boyars_confirmed")
    )
    require(
        failures,
        "cost_amount" not in boyar_council
        and "add_absolutism = -2" not in boyar_council
        and (
            "stability_cost_modifier = -0.1" in boyars_confirmed_mod
            or "stability_cost_modifier = -0.10" in boyars_confirmed_mod
        )
        and "global_unrest = -1" in boyars_confirmed_mod
        and "land_morale = 0.05" in boyars_confirmed_mod,
        "HLC boyar council office confirmation reverted to slow scale cost or weak modifier",
    )

    zaz_reforms = read("common/government_reforms/RIP_ZAZ_government_reforms.txt")
    general_rada = normalized(named_block(zaz_reforms, "zaz_general_rada_reform"))
    require(
        failures,
        "may_recruit_female_generals" not in general_rada
        and "female_advisor_chance" not in general_rada
        and "free_leader_pool = 1" in general_rada
        and "advisor_pool = 1" in general_rada,
        "zaz_general_rada_reform retains female general/advisor modifiers on the Zaporozhian Sich",
    )
    free_host = normalized(named_block(zaz_reforms, "zaz_free_host_reform"))
    require(
        failures,
        "stability_cost_modifier" not in free_host
        and "max_absolutism" not in free_host
        and "cavalry_power = 0.1" in free_host
        and "army_tradition = 0.5" in free_host
        and "republican_tradition = 0.25" in free_host
        and "winning_wars_gives_rt = yes" in free_host
        and "factor = 10" in free_host,
        "zaz_free_host_reform reverted to harsh R10 penalties or weak bonuses",
    )

    uzh = read("common/government_reforms/RIP_UZH_government_reforms.txt")
    for foreign_attribute in ("has_dutch_election", "english_parliament"):
        require(
            failures,
            foreign_attribute not in uzh,
            f"UZH still leaks a foreign country-specific mechanic: {foreign_attribute}",
        )
    komitat = normalized(named_block(uzh, "uzh_komitat_system_reform"))
    palanok = normalized(named_block(uzh, "uzh_palanok_captaincy_reform"))
    require(
        failures,
        "republican_tradition" not in palanok
        and "legitimacy" not in palanok
        and "land_morale = -0.05" in palanok
        and "global_unrest = 1" in palanok,
        "UZH Palanok parties still contain authority modifiers that are no-ops in one government type",
    )
    require(
        failures,
        "factions = {" not in palanok
        and not (ROOT / "common/factions/RIP_uzh_palanok_factions.txt").exists(),
        "UZH Palanok captaincy is back on the vanilla factions system (it is a states_general scale; see tests/check_uzh_states_general.py)",
    )
    republican_komitat = normalized(
        named_block(uzh, "uzh_republican_komitat_system_reform")
    )
    require(
        failures,
        all(token in komitat for token in ("queen = yes", "heir = yes", "royal_marriage = yes"))
        and all(
            token not in republican_komitat
            for token in ("queen = yes", "heir = yes", "royal_marriage = yes")
        ),
        "UZH republican Komitat still receives the monarchical dynastic layer",
    )
    require(
        failures,
        all(
            token not in komitat
            for token in ("republic = yes", "has_term_election = yes", "duration = 8")
        )
        and all(
            token in republican_komitat
            for token in ("republic = yes", "has_term_election = yes", "duration = 8")
        ),
        "UZH monarchical/republican Komitat reforms have swapped republican election flags",
    )
    hlc_reforms = read("common/government_reforms/RIP_HLC_government_reforms.txt")
    crown_and_sejm = normalized(named_block(hlc_reforms, "hlc_crown_and_sejm_reform"))
    require(
        failures,
        "has_term_election" not in crown_and_sejm
        and "is_elective = yes" in crown_and_sejm
        and "has_polish_election = yes" in crown_and_sejm,
        "HLC Crown and Sejm mixes term elections with Polish elective monarchy",
    )
    uhro_palatial = normalized(named_block(uzh, "uzh_palatial_uhro_reform"))
    uhro_republic = normalized(
        named_block(uzh, "uzh_palatial_uhro_republic_reform")
    )
    require(
        failures,
        "legitimacy = 0.5" in uhro_palatial
        and "republican_tradition = 0.25" not in uhro_palatial
        and "republican_tradition = 0.25" in uhro_republic
        and "legitimacy = 0.5" not in uhro_republic
        and "allow = { government =" not in normalized(uzh),
        "UZH Ugro-Rusyn Palatial reform does not use government-appropriate authority",
    )
    synod = normalized(named_block(uzh, "uzh_union_synod_reform"))
    require(
        failures,
        "is_year = 1646 has_country_flag = uzh_union_synod_established" in synod
        and "potential = { OR = { has_reform = uzh_union_synod_reform tag = UZH has_country_flag = uzh_union_synod_established"
        in synod
        and "tag = UZH is_year = 1646" not in synod
        and "has_country_modifier = uz_greek_catholic_concord" not in synod,
        "UZH Union Synod is still gated by an expiring modifier instead of its permanent outcome",
    )
    republic_government = named_block(
        read("common/governments/00_governments.txt"), "republic"
    )
    republic_exclusions = normalized(
        "\n".join(
            block
            for _, block in keyed_blocks(republic_government, "exclusive_reforms")
        )
    )
    require(
        failures,
        "uzh_union_synod_reform" not in republic_exclusions,
        "UZH Union Synod is mutually exclusive with the parliament needed by its Palatial branch",
    )
    uzh_missions_raw = read("missions/Zakarpatta_Missions.txt")
    uzh_missions = normalized(uzh_missions_raw)
    require(
        failures,
        "has_government_attribute = has_dutch_election" not in uzh_missions,
        "UZH mission still tests the removed Dutch election attribute",
    )
    require(
        failures,
        "has_states_general_mechanic = yes"
        in normalized(named_block(uzh_missions_raw, "uzh_komitat_system"))
        and "has_reform = uzh_palanok_captaincy_reform" in uzh_missions
        and "statists_vs_orangists = 0.7" in uzh_missions,
        "UZH Komitat mission does not enforce Captains' Party support for the Palanok mechanic",
    )
    komitat_mission = normalized(named_block(uzh_missions_raw, "uzh_komitat_system"))
    require(
        failures,
        "government = monarchy" in komitat_mission
        and "add_government_reform = uzh_komitat_system_reform" in komitat_mission
        and "government = republic" in komitat_mission
        and "add_government_reform = uzh_republican_komitat_system_reform"
        in komitat_mission,
        "UZH Komitat mission does not grant the government-specific M1/R1 reform",
    )
    uzh_slot = normalized(named_block(read("missions/Zakarpatta_Missions.txt"), "UZH_missions_4"))
    require(
        failures,
        "government = monarchy" in uzh_slot
        and "government = republic" in uzh_slot
        and "government = theocracy" not in uzh_slot,
        "UZH constitutional missions can force M/R-only reforms into an unsupported government type",
    )
    palatial_mission = named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_palatial_reform")
    palatial_requirements = normalized(named_block(palatial_mission, "required_missions"))
    require(
        failures,
        "uzh_rusin_nobility" in palatial_requirements
        and "uz_identity_question" in palatial_requirements,
        "UZH Palatial mission can resolve before an identity path exists",
    )
    identity_question = normalized(
        named_block(uzh_missions_raw, "uz_identity_question")
    )
    pre_identity_culture = normalized(
        named_block(
            read("common/scripted_triggers/uzh_uzh_triggers.txt"),
            "uzh_pre_identity_candidate_culture",
        )
    )
    require(
        failures,
        "uzh_pre_identity_candidate_culture = yes" in identity_question
        and "uzh_identity_core_culture = yes" not in identity_question
        and all(
            f"culture = {culture}" in pre_identity_culture
            and f"primary_culture = {culture}" in identity_question
            for culture in (
                "rusyn",
                "rusyn_new",
                "ruthenian",
                "ruthenian_new",
                "rusyn_new_new",
            )
        ),
        "UZH identity selector still depends on its not-yet-selected identity",
    )
    backa_settlements = normalized(
        named_block(uzh_missions_raw, "uzh_backa_settlements")
    )
    banat_colonization = normalized(
        named_block(uzh_missions_raw, "uzh_banat_colonization")
    )
    require(
        failures,
        "uzh_set_identity_culture = yes" in backa_settlements
        and "uzh_set_identity_culture = yes" in banat_colonization
        and "change_culture = rusyn" not in backa_settlements
        and "change_culture = rusyn" not in banat_colonization,
        "UZH Alföld/Banat settlement still overwrites the selected identity culture",
    )
    palatial_effect = normalized(palatial_mission)
    require(
        failures,
        "government = monarchy } add_government_reform = uzh_palatial_uhro_reform"
        in palatial_effect
        and "government = republic } add_government_reform = uzh_palatial_uhro_republic_reform"
        in palatial_effect,
        "UZH Palatial mission does not grant the government-specific Ugro-Rusyn reform",
    )
    require(
        failures,
        "num_of_owned_provinces_with = { region = carpathia_region has_seat_in_parliament = yes value = 5"
        in palatial_effect
        and "calc_true_if" not in palatial_effect,
        "UZH Palatial mission uses calc_true_if as a province counter and is unreachable",
    )
    rusyn_autonomy = normalized(named_block(uzh_missions_raw, "uz_rusyn_autonomy"))
    carpathian_federation = normalized(
        named_block(uzh_missions_raw, "uz_carpathian_federation")
    )
    carpathian_commonwealth = normalized(
        named_block(uzh_missions_raw, "uz_carpathian_commonwealth")
    )
    require(
        failures,
        "government = republic" not in rusyn_autonomy
        and "government = republic" not in carpathian_federation
        and "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in rusyn_autonomy
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 15"
        in carpathian_federation
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in carpathian_commonwealth,
        "UZH Rusyn identity branch is still republic-locked or gives authority no-ops",
    )
    zakarpattia_realm = normalized(
        named_block(uzh_missions_raw, "uz_zakarpattia_realm")
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in zakarpattia_realm
        and "add_legitimacy = 15" not in zakarpattia_realm
        and "add_republican_tradition = 8" not in zakarpattia_realm,
        "UZH early realm mission still gives government-specific authority no-ops",
    )
    pressburg = normalized(named_block(uzh_missions_raw, "uz_pressburg_compact"))
    saint_stephen = normalized(
        named_block(uzh_missions_raw, "uz_crown_of_saint_stephen")
    )
    require(
        failures,
        "legitimacy_equivalent = 70" in pressburg
        and "legitimacy = 70" not in pressburg
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in pressburg
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 7"
        in saint_stephen,
        "UZH Ugro-Rusyn branch still blocks republics or gives authority no-ops",
    )
    require(
        failures,
        "owns_or_subject_of = 1772" in pressburg
        and "region = carpathia_region value = 8" in pressburg,
        "UZH Pressburg Compact has no regional-sovereignty route if Hungary disappears",
    )
    uhro_integration = normalized(
        named_block(uzh_missions_raw, "uz_uhro_rusyn_integration")
    )
    danubian_ascendancy = normalized(
        named_block(uzh_missions_raw, "uz_danubian_monarchy")
    )
    require(
        failures,
        "owns_or_subject_of = 1772" in uhro_integration
        and "region = carpathia_region value = 8" in uhro_integration
        and "owns_or_subject_of = 153" in danubian_ascendancy
        and "owns_or_subject_of = 1772" in danubian_ascendancy
        and "region = carpathia_region value = 15" in danubian_ascendancy,
        "UZH Ugro-Rusyn branch still becomes unreachable after Hungary is conquered or inherited",
    )
    revival = normalized(named_block(uzh_missions_raw, "uz_national_revival"))
    require(
        failures,
        "has_reform = uzh_komitat_system_reform" in revival
        and "has_reform = uzh_republican_komitat_system_reform" in revival,
        "UZH revival mission does not recognize both Komitat variants",
    )
    rusyn_state_mission = normalized(
        named_block(uzh_missions_raw, "uz_rusin_state")
    )
    require(
        failures,
        "is_subject = no" in rusyn_state_mission
        and "total_development = 200" in rusyn_state_mission
        and "has_country_flag = uzh_revival_complete" in rusyn_state_mission,
        "UZH can proclaim its sovereign Rusyn State capstone while still a subject",
    )
    srem = normalized(named_block(uzh_missions_raw, "uzh_srem_metropolis"))
    require(
        failures,
        "4173" in srem
        and "2960" not in srem
        and "religion = ROOT" in srem
        and "limit = { religion = catholic } add_papal_influence = 15" in srem
        and "else = { rip_faith_mission_resource_effect = { PA = 0.15 PI = 15 ADM = 25 }" in srem,
        "UZH Srem Metropolis has the wrong province or gives a faith-currency no-op",
    )
    security_congress = normalized(
        named_block(uzh_missions_raw, "uz_resist_habsburgs")
    )
    require(
        failures,
        "government = monarchy num_of_royal_marriages = 1" in security_congress
        and "government = republic OR = { diplomatic_reputation = 2 republican_tradition = 70"
        in security_congress
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in security_congress
        and "uzh_select_dynasty_patron_unlocked" not in security_congress,
        "UZH Palanok security mission remains monarchy-locked or advertises a missing decision",
    )
    union_mission = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uz_union_dilemma")
    )
    preserve_faith = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uz_preserve_orthodox_faith")
    )
    require(
        failures,
        "set_country_flag = uzh_union_synod_established" in union_mission
        and "is_year = 1646" in union_mission
        and "government = monarchy government = republic" in union_mission
        and "add_government_reform = uzh_union_synod_reform" in union_mission
        and "set_country_flag = uzh_union_old_rite_confirmed" in union_mission,
        "UZH religious mission outcomes do not persist or grant their supported Synod reform",
    )
    require(
        failures,
        "religion = greek_catholic" in preserve_faith
        and "religion = greek_catholic" in union_mission
        and "limit = { religion = catholic } add_papal_influence = 25" in union_mission
        and "limit = { religion = greek_catholic } rip_faith_mission_resource_effect = { PA = 0.15 PI = 15 ADM = 25 }"
        in union_mission,
        "UZH mission tree excludes its own Greek Catholic religious path",
    )
    rite_settlement = normalized(
        named_block(uzh_missions_raw, "uz_orthodox_unity")
    )
    require(
        failures,
        "religion = orthodox religion = russian_orthodox religion = greek_catholic" in rite_settlement
        and "religion = catholic papal_influence = 50" in rite_settlement
        and "religion = ROOT uzh_identity_core_culture = yes value = 8"
        in rite_settlement
        and "limit = { religion = catholic } add_papal_influence = 25"
        in rite_settlement
        and "else = { rip_faith_mission_resource_effect = { PA = 0.25 PI = 25 ADM = 25 }" in rite_settlement,
        "UZH Ruthenian identity branch still requires Orthodox-only currency or provinces",
    )
    uzh_modifiers_raw = read("common/event_modifiers/RIP_UZH_modifiers.txt")
    uzh_modifiers = normalized(named_block(uzh_modifiers_raw, "orthodox_zeal"))
    require(
        failures,
        "papal_influence" not in uzh_modifiers,
        "Ruthenian rite settlement still penalizes the Catholic path it now supports",
    )
    for modifier_id in (
        "uz_pannonian_autonomy",
        "uz_pannonian_league",
        "uz_slavo_rusyn_identity",
        "uz_carpathian_commonwealth",
        "uz_sovereign_rusin_state",
        "uz_pressburg_compact",
        "uz_crown_of_saint_stephen",
        "uz_rusyn_autonomy",
        "uz_kyivan_legacy",
        "uz_rusyn_self_governance",
    ):
        modifier = normalized(named_block(uzh_modifiers_raw, modifier_id))
        require(
            failures,
            "legitimacy =" not in modifier
            and "republican_tradition =" not in modifier,
            f"cross-government UZH modifier has an authority no-op: {modifier_id}",
        )
    constitutional_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_constitutional_system")
    )
    require(
        failures,
        "legitimacy = 0.5" in constitutional_modifier
        and "republican_tradition =" not in constitutional_modifier,
        "monarchy-only UZH constitutional modifier lost its coherent authority reward",
    )
    basilian_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_basilian_monasteries")
    )
    karloca_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_karloca_synod_blessing")
    )
    require(
        failures,
        "papal_influence" not in basilian_modifier
        and "tolerance_own = 1" in basilian_modifier
        and "yearly_patriarch_authority" not in karloca_modifier
        and "church_loyalty_modifier = 0.1" in karloca_modifier,
        "UZH permanent rite modifiers still give a supported faith a dead currency",
    )
    tisza_customs = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_tisza_customs_convention")
    )
    require(
        failures,
        "134 = { is_strongest_trade_power = ROOT" in tisza_customs
        and "137 = { is_strongest_trade_power = ROOT" in tisza_customs
        and not re.search(r"\b(?:118|120|121|122|123|124)\b", tisza_customs),
        "UZH Tisza Customs checks provinces outside the stated Wien/Ragusa trade nodes",
    )
    federative_statutes = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_federative_statutes")
    )
    require(
        failures,
        "num_of_subjects = 2" in federative_statutes
        and "NOT = { any_subject_country = { liberty_desire = 50" in federative_statutes
        and "calc_true_if" not in federative_statutes,
        "UZH Federative Statutes uses calc_true_if as a subject counter and is unreachable",
    )
    federalization = named_block(uzh_missions_raw, "uzh_federalization")
    federal_requirements = normalized(named_block(federalization, "required_missions"))
    federal_trigger = normalized(named_block(federalization, "trigger"))
    require(
        failures,
        "uzh_pannonian_republic" in federal_requirements
        and "uzh_constitutional_monarchy" not in federal_requirements
        and "has_country_flag = uzh_constitutional_framework" in federal_trigger
        and "has_country_flag = uzh_pannonian_compact_signed" in federal_trigger
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in normalized(federalization)
        and "add_legitimacy = 10" not in normalized(federalization)
        and "add_republican_tradition = 15" not in normalized(federalization),
        "UZH Federalization still requires mutually exclusive monarchy and republic missions",
    )
    uzh_events = read("events/Uzh.txt")
    rite_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.1\b", normalized(block))
        )
    )
    karloca_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh.201" in normalized(block)
        )
    )
    security_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.5\b", normalized(block))
        )
    )
    rusyn_state_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.8\b", normalized(block))
        )
    )
    constitutional_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.52\b", normalized(block))
        )
    )
    rusyn_identity_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.3" in normalized(block)
        )
    )
    require(
        failures,
        "limit = { religion = catholic } add_papal_influence = 10" in rite_event
        and "else = { add_patriarch_authority = 0.1" in rite_event
        and "limit = { religion = catholic } add_papal_influence = 10"
        in karloca_event
        and "else = { add_patriarch_authority = 0.05" in karloca_event,
        "UZH Carpathian rite events still give Catholics Patriarch Authority no-ops",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in security_event
        and "add_legitimacy = 10" not in security_event
        and "add_republican_tradition = 5" not in security_event,
        "UZH security congress follow-up still gives government-specific authority no-ops",
    )
    require(
        failures,
        all(f"add_{power}_power = 150" in rusyn_state_event for power in ("adm", "dip", "mil"))
        and "add_adm_power = 400" not in rusyn_state_event
        and "limit = { NOT = { government_rank = 2 } } set_government_rank = 2"
        in rusyn_state_event,
        "UZH Rusyn State capstone remains over-rewarded or can downgrade an empire",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in constitutional_event
        and "add_legitimacy = 10" not in constitutional_event
        and "add_republican_tradition = 5" not in constitutional_event
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 15"
        in rusyn_identity_event
        and "add_republican_tradition = 15" not in rusyn_identity_event,
        "UZH constitutional/identity events still give government-specific authority no-ops",
    )
    identity_choice_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.1" in normalized(block)
        )
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in identity_choice_event
        and "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in identity_choice_event
        and "add_legitimacy = 10" not in identity_choice_event
        and "add_republican_tradition = 10" not in identity_choice_event,
        "UZH identity choices still give monarchy- or republic-only authority no-ops",
    )
    synod_event_raw = next(
        block
        for _, block in keyed_blocks(uzh_events, "country_event")
        if re.search(r"\bid = uzh\.51\b", normalized(block))
    )
    synod_event = normalized(synod_event_raw)
    require(
        failures,
        "set_country_flag = uzh_union_synod_established" in synod_event
        and "government = monarchy government = republic" in synod_event
        and "add_government_reform = uzh_union_synod_reform" in synod_event
        and "set_country_flag = uzh_union_old_rite_confirmed" in synod_event,
        "UZH 1646 union event outcomes do not persist or grant their supported Synod reform",
    )
    synod_event_trigger = normalized(named_block(synod_event_raw, "trigger"))
    require(
        failures,
        "religion = orthodox" in synod_event_trigger
        and "religion = catholic" in synod_event_trigger
        and "religion = greek_catholic" in synod_event_trigger
        and "religion_group = christian" not in synod_event_trigger,
        "UZH Union of Uzhhorod event is available to narratively incompatible Christian faiths",
    )
    ruthenian_identity_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.2" in normalized(block)
        )
    )
    require(
        failures,
        "limit = { religion = catholic } add_papal_influence = 15"
        in ruthenian_identity_event
        and "else = { add_patriarch_authority = 0.1" in ruthenian_identity_event
        and "religion = ROOT uzh_identity_core_culture = yes"
        in ruthenian_identity_event,
        "UZH Ruthenian identity consequence still gives Catholics a Patriarch Authority no-op",
    )
    synod_migration_raw = next(
        block
        for _, block in keyed_blocks(uzh_events, "country_event")
        if re.search(r"\bid = uzh\.204\b", normalized(block))
    )
    synod_migration = normalized(synod_migration_raw)
    require(
        failures,
        "hidden = yes" in synod_migration
        and "mean_time_to_happen = { days = 1 }" in synod_migration
        and "has_country_modifier = uz_greek_catholic_concord" in synod_migration
        and "set_country_flag = uzh_union_synod_established" in synod_migration
        and "has_country_modifier = uz_old_rite_resilience" in synod_migration
        and "set_country_flag = uzh_union_old_rite_confirmed" in synod_migration,
        "UZH old saves with active union outcomes are not migrated to permanent flags",
    )
    migration_trigger = normalized(named_block(synod_migration_raw, "trigger"))
    require(
        failures,
        migration_trigger.startswith("trigger = { OR = {")
        and "tag = UZH" not in synod_migration
        and "government = republic has_reform = uzh_komitat_system_reform"
        in migration_trigger
        and "government = republic has_reform = uzh_palatial_uhro_reform"
        in migration_trigger
        and "remove_government_reform = uzh_komitat_system_reform"
        in synod_migration
        and "add_government_reform = uzh_republican_komitat_system_reform"
        in synod_migration
        and "remove_government_reform = uzh_palatial_uhro_reform"
        in synod_migration
        and "add_government_reform = uzh_palatial_uhro_republic_reform"
        in synod_migration,
        "UZH descendant republic saves do not migrate the old shared reform IDs",
    )
    gov_names = read("common/government_names/000_RIP_names.txt")
    uz_name = normalized(named_block(gov_names, "uzh_komitat_system_reform"))
    require(
        failures,
        "has_reform = uzh_komitat_system_reform" in uz_name
        and "has_reform = uzh_republican_komitat_system_reform" in uz_name,
        "UZH Komitat government name does not recognize the republican reform ID",
    )
    uzh_eparchy_name = normalized(
        named_block(gov_names, "uzh_mukachevo_eparchy_reform")
    )
    require(
        failures,
        "has_reform = uzh_mukachevo_eparchy_reform" in uzh_eparchy_name
        and "has_reform = uzh_uzhhorod_seat_translation_reform" in uzh_eparchy_name
        and "has_reform = uzh_presov_eparchy_reform" in uzh_eparchy_name,
        "UZH eparchy government name does not recognize its Th2/Th3 reform IDs",
    )
    vln_hetman_titles = (
        "vln_black_voivode_legion",
        "vln_confessional_reform",
        "vln_confessional_academy",
        "vln_cossack_host_reform",
    )
    m7_m8_guard = (
        "NOT = { OR = { has_reform = vln_ruthenian_renaissance_reform "
        "has_reform = vln_magdeburg_rights } }"
    )
    name_blocks = set(re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", gov_names))
    for reform in ("vln_ruthenian_renaissance_reform", "vln_magdeburg_rights"):
        guards = [
            normalized(named_block(gov_names, title))
            for title in vln_hetman_titles
        ]
        require(
            failures,
            reform not in name_blocks
            and all(m7_m8_guard in title for title in guards)
            and normalized(gov_names).count(f"has_reform = {reform}")
            == len(vln_hetman_titles),
            f"{reform} must only suppress earlier Hetman titles, not define a new government name",
        )
    require(
        failures,
        "CULTURED_HETMAN" not in gov_names and "BURGOMASTER_HETMAN" not in gov_names,
        "shared M7/M8 reforms still introduce new Hetman titles in 000_RIP_names.txt",
    )
    for pdl_name_id in (
        "pdl_grand_podillia",
        "pdl_absolute_dominion",
        "pdl_magnate_republic",
        "pdl_magnate_dominion",
        "pdl_enlightened_voivodeship",
        "pdl_revolutionary_republic",
        "pdl_carpathian_bastion",
        "pdl_frontier_republic",
        "pdl_palatine_court",
        "pdl_aristocratic_assembly",
        "pdl_clan_assembly",
        "pdl_steppe_principality",
        "pdl_voivodeship_kingdom",
        "pdl_frontier_voivodeship",
    ):
        pdl_name_trigger = normalized(
            named_block(named_block(gov_names, pdl_name_id), "trigger")
        )
        require(
            failures,
            "west_ukraine_pdl_origin_country = yes" in pdl_name_trigger
            and "tag = PDL" not in pdl_name_trigger
            and f"has_reform = {pdl_name_id}_reform" in pdl_name_trigger,
            f"PDL government name {pdl_name_id} is tag-locked or missing its reform check",
        )
    uzh_eparchy_reforms = read("common/government_reforms/RIP_UZH_government_reforms.txt")
    seat_translation = normalized(named_block(uzh_eparchy_reforms, "uzh_uzhhorod_seat_translation_reform"))
    presov_split = normalized(named_block(uzh_eparchy_reforms, "uzh_presov_eparchy_reform"))
    require(
        failures,
        "has_reform = uzh_mukachevo_eparchy_reform" in seat_translation
        and "has_reform = uzh_uzhhorod_seat_translation_reform" in presov_split
        and "is_year = 1771" not in seat_translation
        and "is_year = 1771" not in presov_split,
        "UZH eparchy Th2/Th3 reforms do not chain from Th1 or duplicate its 1771 gate",
    )
    uzh_eparchy_path = read("decisions/UzhEparchyPath.txt")
    seat_translate_decision = normalized(named_block(uzh_eparchy_path, "uzh_translate_the_episcopal_seat"))
    presov_decision = normalized(named_block(uzh_eparchy_path, "uzh_establish_the_presov_eparchy"))
    require(
        failures,
        "has_reform = uzh_mukachevo_eparchy_reform" in seat_translate_decision
        and "has_reform = uzh_uzhhorod_seat_translation_reform" in presov_decision
        and "is_year = 1818" in presov_decision,
        "UZH eparchy Th2/Th3 decisions do not gate on the prior tier's reform",
    )
    for path in (
        "localisation/RIP_l_english.yml",
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    ):
        locale = read(path)
        require(
            failures,
            re.search(
                r"(?m)^\s*(?:statists|orangists)(?:_influence|_FACTION_DESC)?:\d+\s+",
                locale,
            )
            is None,
            f"UZH still globally renames the vanilla Dutch factions in {path}",
        )
    english = read("localisation/RIP_l_english.yml")
    fallback_paths = (
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    )
    for key in (
        "uzh_palanok_captaincy_reform_desc",
        "uzh_komitat_system_reform_desc",
        "uzh_republican_komitat_system_reform",
        "uzh_republican_komitat_system_reform_desc",
        "uzh_palatial_ruthenian_reform",
        "uzh_palatial_ruthenian_reform_desc",
        "uzh_palatial_uhro_reform_desc",
        "uzh_palatial_uhro_republic_reform",
        "uzh_palatial_uhro_republic_reform_desc",
        "boyar_elite_reform_desc",
        "uz_danubian_monarchy_title",
        "uz_danubian_monarchy_desc",
        "danubian_monarchy_influence",
        "desc_danubian_monarchy_influence",
        "UZH_orthodox_unity_culture_tt",
        "uz_orthodox_unity_title",
        "uz_orthodox_unity_desc",
        "orthodox_zeal",
        "desc_orthodox_zeal",
        "uz_orthodox_metropolis",
        "desc_uz_orthodox_metropolis",
        "uz_orthodox_revival",
        "desc_uz_orthodox_revival",
        "uzh_identity.2.a",
        "uzh_identity.2.d",
        "uz_pressburg_compact_desc",
        "desc_uz_pressburg_compact",
        "uz_preserve_orthodox_faith_title",
        "uz_preserve_orthodox_faith_desc",
        "uzh.1.t",
        "uzh.1.d",
        "uzh.1.a",
        "uzh_srem_metropolis_desc",
        "desc_uz_ruthenian_awakening",
        "UZH_resist_habsburgs_base_tt",
        "UZH_resist_habsburgs_habsburg_tt",
        "uz_resist_habsburgs_title",
        "uz_resist_habsburgs_desc",
        "uz_border_dynasty_network",
        "desc_uz_border_dynasty_network",
        "opinion_uz_border_dynasty",
        "uzh.5.t",
        "uzh.5.d",
        "uzh.5.a",
        "uzh.5.b",
        "partia_soymu_MECHANIC_TOOLTIP",
        "partia_kapitaniv_MECHANIC_TOOLTIP",
        "UZH_federalization_authority_tt",
        "uz_rusin_state_title",
        "uz_rusin_state_desc",
        "uz_crown_of_saint_stephen",
        "uz_crown_of_saint_stephen_title",
        "uz_crown_of_saint_stephen_desc",
        "uzh.8.d",
        "uzh_identity.3.d",
        "uzh_identity.3.a",
        "desc_uz_crown_of_saint_stephen",
        "desc_uz_slavo_rusyn_identity",
        "desc_uz_pannonian_autonomy",
        "desc_uz_pannonian_league",
        "desc_uz_kyivan_legacy",
        "desc_uz_carpathian_federation",
        "desc_uz_karloca_synod_blessing",
    ):
        match = re.search(rf'(?m)^\s*{key}:\d+\s+"([^"]*)"', english)
        require(failures, match is not None, f"missing English narrative key: {key}")
        if match is None:
            continue
        for path in fallback_paths:
            fallback = read(path)
            fallback_match = re.search(rf'(?m)^\s*{key}:\d+\s+"([^"]*)"', fallback)
            require(
                failures,
                fallback_match is not None and fallback_match.group(1) == match.group(1),
                f"fallback copy does not match English for {key}: {path}",
            )
    require(
        failures,
        "hereditary Palanok captaincy" not in english
        and "Palatinate of Three Nations" not in english
        and "kings cannot rule alone, and needs" not in english
        and "our chosen identity" not in english
        and 'uz_danubian_monarchy_title:0 "Danubian Monarchy"' not in english
        and 'uz_crown_of_saint_stephen_title:0 "Crown of Saint Stephen"' not in english
        and "As an independent nation" not in english
        and "multicultural republic" not in english
        and "republican institutions" not in english
        and "Patriarchal favor warms our altars" not in english,
        "UZH/Ruthenian reform localisation retains the audited narrative or grammar defect",
    )

    podillia = read("decisions/Podillia_Decisions.txt")
    require(failures, "change_tag = RUS" not in podillia, "unsafe duplicate PDL-to-Russia formable remains")
    galician_union = normalized(named_block(podillia, "pdl_unite_with_galicia_diplo"))
    require(
        failures,
        "inherit = HLC" in galician_union and "change_tag = HLC" not in galician_union,
        "Podillian diplomatic union still discards its reform path by changing into HLC",
    )

    ruthenia = normalized(read("decisions/RuthenianNation.txt"))
    ukr_change = ruthenia.find("change_tag = UKR")
    ukr_swap = ruthenia.find("swap_non_generic_missions = yes", ukr_change)
    ukr_change_effect = ruthenia.find("on_change_tag_effect = yes", ukr_change)
    require(
        failures,
        ukr_change < ukr_swap < ukr_change_effect,
        "UKR formation does not call the vanilla tag-change effect after swapping missions",
    )
    for source_tag, origin_flag in (
        ("HLC", "rip_vol_origin_hlc"),
        ("VLN", "rip_vol_origin_vln"),
        ("PDL", "rip_vol_origin_pdl"),
    ):
        origin = ruthenia.find(
            f"limit = {{ tag = {source_tag} }} set_country_flag = {origin_flag}"
        )
        require(
            failures,
            origin >= 0 and ukr_change >= 0 and origin < ukr_change,
            f"direct {source_tag}-to-UKR formation loses its reform lineage",
        )
    hlc_path_recovery = ruthenia.find(
        "has_country_flag = rip_vol_origin_hlc "
        "NOT = { hlc_has_any_path = yes } } "
        "country_event = { id = rip_galicia.1 days = 1 }"
    )
    require(
        failures,
        hlc_path_recovery > ukr_change,
        "HLC-origin UKR can lose the only event that selects its foundational reform path",
    )

    hetmanate_nation = named_block(read("decisions/HetmanateNation.txt"), "hetmanate_nation")
    hetmanate_potential = normalized(named_block(hetmanate_nation, "potential"))
    require(
        failures,
        "tag = PRL" in hetmanate_potential
        and "tag = ZAZ government = republic" in hetmanate_potential,
        "a sacred-order or sacred-horde ZAZ can still enter the republican HET tree",
    )
    hetmanate_decisions = read("decisions/HetmanateDecisions.txt")
    for decision_id in (
        "het_establish_regiments",
        "het_expand_academy",
        "het_reform_elections",
    ):
        decision = named_block(hetmanate_decisions, decision_id)
        potential = normalized(named_block(decision, "potential"))
        require(
            failures,
            "tag = HET" in potential and "government = republic" in potential,
            f"republic-only HET mechanics leak into another government: {decision_id}",
        )

    for path, target_tag in (
        ("decisions/KyivTriggers.txt", "KRU"),
        ("decisions/VHKNation.txt", "VOL"),
        ("decisions/HetmanateNation.txt", "HET"),
        ("decisions/KuyabaNation.txt", "KUY"),
        ("decisions/PolesianBelarusianNations.txt", "RPS"),
        ("decisions/PolesianBelarusianNations.txt", "PLT"),
        ("decisions/PolesianBelarusianNations.txt", "BLR"),
    ):
        transition = normalized(read(path))
        change = transition.find(f"change_tag = {target_tag}")
        swap = transition.find("swap_non_generic_missions = yes", change)
        on_change = transition.find("on_change_tag_effect = yes", swap)
        require(
            failures,
            change >= 0 and change < swap < on_change,
            f"{target_tag} formation does not finish the vanilla mission/tag-change lifecycle",
        )
    lineage_gates = read("common/scripted_triggers/rip_path_state_triggers.txt")
    top_level_triggers = Counter(
        re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", lineage_gates)
    )
    duplicate_triggers = sorted(
        name for name, count in top_level_triggers.items() if count > 1
    )
    require(
        failures,
        not duplicate_triggers,
        f"duplicate scripted trigger definition(s) in rip_path_state_triggers.txt: {', '.join(duplicate_triggers)}",
    )
    for gate in (
        "west_ukraine_hlc_origin_country",
        "west_ukraine_vln_origin_country",
        "west_ukraine_pdl_origin_country",
    ):
        gate_blocks = [normalized(block) for _, block in keyed_blocks(lineage_gates, gate)]
        require(
            failures,
            len(gate_blocks) == 1 and "tag = UKR" in gate_blocks[-1],
            f"UKR cannot continue its inherited western reform lineage: {gate}",
        )

    pdl_reforms = read("common/government_reforms/RIP_PDL_government_reforms.txt")
    pdl_absolute = normalized(named_block(pdl_reforms, "pdl_absolute_dominion_reform"))
    pdl_enlightened = normalized(
        named_block(pdl_reforms, "pdl_enlightened_voivodeship_reform")
    )
    pdl_popular = normalized(named_block(pdl_reforms, "pdl_revolutionary_republic_reform"))
    require(
        failures,
        "pdl_magnate_reforms_visible = yes" in pdl_absolute
        and "pdl_frontier_reform_visible = yes" not in pdl_absolute,
        "PDL Absolute Dominion is not confined to the magnate path",
    )
    require(
        failures,
        "pdl_frontier_reform_visible = yes" in pdl_popular
        and "current_age = age_of_revolutions" in pdl_popular,
        "PDL Popular Sovereignty lacks its frontier path or late-era gate",
    )
    require(
        failures,
        "pdl_carpathian_reform_visible = yes" in pdl_enlightened
        and "has_institution = enlightenment" in pdl_enlightened,
        "PDL Enlightened Voivodeship lacks its Dniester path or Enlightenment gate",
    )
    pdl_gates = read("common/scripted_triggers/pdl_pdl_reform_triggers.txt")
    pdl_magnate_gate = normalized(named_block(pdl_gates, "pdl_magnate_reforms_visible"))
    require(
        failures,
        "has_reform = pdl_absolute_dominion_reform" in pdl_magnate_gate
        and "has_reform = pdl_palatine_court_reform" not in pdl_magnate_gate,
        "PDL magnate self-gate leaks into the Dniester path",
    )

    pdl_history = normalized(read("history/countries/PDL - Podillia.txt"))
    vln_history = normalized(read("history/countries/VLN - Voln.txt"))
    require(
        failures,
        "add_government_reform = pdl_frontier_voivodeship_reform" in pdl_history
        and "add_government_reform = feudalism_reform" not in pdl_history,
        "PDL still starts without its unique fallback reform",
    )
    require(
        failures,
        "add_government_reform = vln_voivodeship_reform" in vln_history
        and "add_government_reform = feudalism_reform" not in vln_history,
        "VLN still starts without its unique voivodeship reform",
    )
    for base_reform in (
        "pdl_clan_assembly_reform",
        "pdl_steppe_principality_reform",
        "pdl_voivodeship_kingdom_reform",
        "pdl_frontier_voivodeship_reform",
    ):
        require(
            failures,
            "lock_level_when_selected = yes"
            in normalized(named_block(pdl_reforms, base_reform)),
            f"PDL path base does not lock its first tier: {base_reform}",
        )

    for base_reform, path_flag in (
        ("pdl_clan_assembly_reform", "pdl_frontier_path"),
        ("pdl_steppe_principality_reform", "pdl_carpathian_path"),
        ("pdl_voivodeship_kingdom_reform", "pdl_magnate_path"),
    ):
        reform_block = named_block(pdl_reforms, base_reform)
        expected_gate = normalized(
            f"""
            OR = {{
                has_reform = {base_reform}
                AND = {{
                    west_ukraine_pdl_origin_country = yes
                    has_country_flag = {path_flag}
                }}
            }}
            """
        )
        for gate_name in ("potential", "trigger"):
            gate = normalized(named_block(reform_block, gate_name))
            require(
                failures,
                expected_gate in gate and "tag = PDL" not in gate,
                f"{base_reform} {gate_name} is not restricted to its PDL-origin path: {path_flag}",
            )

    fallback = named_block(pdl_reforms, "pdl_frontier_voivodeship_reform")
    fallback_gate = normalized(
        """
        OR = {
            has_reform = pdl_frontier_voivodeship_reform
            AND = {
                west_ukraine_pdl_origin_country = yes
                NOT = { has_country_flag = pdl_carpathian_path }
                NOT = { has_country_flag = pdl_frontier_path }
                NOT = { has_country_flag = pdl_magnate_path }
            }
        }
        """
    )
    for gate_name in ("potential", "trigger"):
        gate = normalized(named_block(fallback, gate_name))
        require(
            failures,
            fallback_gate in gate and "tag = PDL" not in gate,
            f"PDL fallback {gate_name} does not preserve its current holders and no-path lineage access",
        )
    pdl_origin_trigger = normalized(
        named_block(
            read("common/scripted_triggers/rip_path_state_triggers.txt"),
            "west_ukraine_pdl_origin_country",
        )
    )
    require(
        failures,
        all(
            token in pdl_origin_trigger
            for token in (
                "tag = PDL",
                "tag = VOL",
                "tag = UKR",
                "has_country_flag = rip_vol_origin_pdl",
            )
        ),
        "PDL-origin reform gates no longer follow PDL lineage through VOL/UKR",
    )

    royal_voivodeship_modifiers = normalized(
        named_block(
            named_block(pdl_reforms, "pdl_voivodeship_kingdom_reform"),
            "modifiers",
        )
    )
    frontier_voivodeship_modifiers = normalized(
        named_block(
            named_block(pdl_reforms, "pdl_frontier_voivodeship_reform"),
            "modifiers",
        )
    )
    require(
        failures,
        "governing_capacity_modifier = 0.1" in royal_voivodeship_modifiers
        and "reform_progress_growth = 0.1" in royal_voivodeship_modifiers
        and "state_maintenance_modifier = -0.1" in royal_voivodeship_modifiers
        and "fort_maintenance_modifier" not in royal_voivodeship_modifiers
        and "governing_capacity_modifier = 0.1" in frontier_voivodeship_modifiers
        and "reform_progress_growth = 0.1" in frontier_voivodeship_modifiers
        and "fort_maintenance_modifier = -0.1" in frontier_voivodeship_modifiers
        and "state_maintenance_modifier" not in frontier_voivodeship_modifiers,
        "PDL Royal and Frontier Voivodeships do not have distinct, doctrine-aligned upkeep modifiers",
    )

    pdl_decisions = read("decisions/Podillia_Decisions.txt")
    for decision, flag, reform in (
        ("pdl_adopt_carpathian_doctrine", "pdl_carpathian_path", "pdl_steppe_principality_reform"),
        ("pdl_adopt_cossack_traditions", "pdl_frontier_path", "pdl_clan_assembly_reform"),
        ("pdl_adopt_magnate_governance", "pdl_magnate_path", "pdl_voivodeship_kingdom_reform"),
    ):
        block = named_block(pdl_decisions, decision)
        potential = normalized(named_block(block, "potential"))
        ai_will_do = normalized(named_block(block, "ai_will_do"))
        normalized_block = normalized(block)
        flag_pos = normalized_block.find(f"set_country_flag = {flag}")
        reform_pos = normalized_block.find(f"add_government_reform = {reform}")
        require(
            failures,
            flag_pos >= 0 and reform_pos >= 0 and flag_pos < reform_pos,
            f"PDL path does not set its gate before replacing the base reform: {decision}",
        )
        require(
            failures,
            "west_ukraine_pdl_origin_country = yes" in potential
            and "tag = PDL" not in potential
            and all(
                f"NOT = {{ has_country_flag = {path_flag} }}" in potential
                for path_flag in (
                    "pdl_carpathian_path",
                    "pdl_frontier_path",
                    "pdl_magnate_path",
                )
            ),
            f"PDL-origin VOL/UKR cannot make one exclusive path choice: {decision}",
        )
        require(
            failures,
            re.search(r"\bfactor\s*=\s*[1-9]", ai_will_do) is not None,
            f"PDL path selector has no positive AI weight: {decision}",
        )

    migration = read("common/scripted_effects/pdl_government_effects.txt")
    normalized_migration = normalized(
        migration + read("common/scripted_effects/vln_government_effects.txt")
    )
    startup = normalized(read("common/on_actions/west_ukraine_on_actions.txt"))
    for effect in ("pdl_reconcile_base_reform_effect", "vln_reconcile_base_reform_effect"):
        require(
            failures,
            effect in normalized_migration and f"{effect} = yes" in startup,
            f"old-save base-reform reconciliation is not wired: {effect}",
        )
    legacy_union = normalized(named_block(migration, "pdl_migrate_legacy_galician_union_effect"))
    require(
        failures,
        "tag = HLC" in legacy_union
        and "has_country_flag = pdl_united_with_galicia" in legacy_union
        and "NOT = { exists = PDL }" in legacy_union
        and "change_tag = PDL" in legacy_union
        and "add_government_reform = hlc_galician_voivodeship_reform" in legacy_union
        and "country_event = { id = rip_galicia.1 days = 1 }" in legacy_union
        and "tag = VOL tag = UKR" in legacy_union
        and "clr_country_flag = rip_vol_origin_hlc" in legacy_union
        and "clr_country_flag = rip_vol_origin_vln" in legacy_union
        and "set_country_flag = rip_vol_origin_pdl" in legacy_union
        and "pdl_migrate_legacy_galician_union_effect = yes" in startup,
        "old saves from the broken PDL-to-HLC union are not migrated safely",
    )
    galicia_event = normalized(named_block(read("events/RIP_Galicia_AltHistory.txt"), "country_event"))
    require(
        failures,
        "id = rip_galicia.1" in galicia_event
        and "NOT = { hlc_has_any_path = yes }" in galicia_event
        and "fire_only_once = yes" not in galicia_event,
        "HLC foundational path selector remains globally one-shot or can repeat after selection",
    )

    odesa = normalized(named_block(read("decisions/OdesaGovernmentDecisions.txt"), "establish_hajibey_free_port"))
    for token in (
        "has_institution = global_trade",
        "change_tag = ODS",
        "change_government = republic",
        "add_government_reform = odesa_trade_republic_reform",
    ):
        require(failures, token in odesa, f"Odesa alternative path lacks {token}")
    require(
        failures,
        odesa.find("swap_non_generic_missions = yes")
        < odesa.find("on_change_tag_effect = yes"),
        "Odesa formation calls the vanilla tag-change effect before swapping missions",
    )

    rank_two_gate = "limit = { NOT = { government_rank = 2 } } set_government_rank = 2"
    cossack_host = normalized(
        named_block(read("decisions/CossackHostDecisions.txt"), "form_cossack_host")
    )
    great_chernihiv = normalized(
        named_block(
            read("common/scripted_effects/chr_path_effects.txt"),
            "chr_proclaim_great_chernihiv_effect",
        )
    )
    prl_missions = read("missions/Pereiaslav_Missions.txt")
    prl_vassal_management = normalized(
        named_block(prl_missions, "prl_vassal_management")
    )
    prl_regional_hegemony = normalized(
        named_block(prl_missions, "prl_regional_hegemony")
    )
    require(
        failures,
        rank_two_gate in cossack_host
        and "government_rank = 1" not in cossack_host
        and rank_two_gate in great_chernihiv
        and "government_rank = 1" not in great_chernihiv
        and rank_two_gate in prl_regional_hegemony,
        "a Cossack/CHR/PRL rank-two reward can downgrade an empire",
    )
    chernihiv_events = normalized(read("events/Chernihiv.txt"))
    chernihiv_independence = normalized(
        named_block(read("missions/Chernihiv_Missions.txt"), "chr_independence")
    )
    require(
        failures,
        "add_legitimacy =" not in chernihiv_events
        and chernihiv_events.count("add_legitimacy_equivalent =") >= 4
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 30"
        in chernihiv_independence
        and "add_legitimacy = 30" not in chernihiv_independence
        and "add_republican_tradition = 30" not in chernihiv_independence,
        "CHR missions/events give the reachable republic path legitimacy no-ops",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in prl_vassal_management
        and "add_legitimacy = 20" not in prl_vassal_management,
        "PRL vassal-management mission gives its republican path a legitimacy no-op",
    )
    prl_events = read("events/PereiaslavFlavor.txt")
    prl_council_event = normalized(
        named_block(prl_events, "country_event", occurrence=1)
    )
    prl_statute_event = normalized(
        named_block(prl_events, "country_event", occurrence=2)
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in prl_council_event
        and "add_legitimacy = 10" not in prl_council_event
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in prl_statute_event
        and "add_legitimacy = 10" not in prl_statute_event,
        "PRL flavor events give the Regimental Republic a legitimacy no-op",
    )


def check_linked_lifecycle(failures: list[str]) -> None:
    het = normalized(read("decisions/HetmanateDecisions.txt"))
    regimental_flag = het.find("set_country_flag = regiments_established")
    regimental_reform = het.find("add_government_reform = het_regimental_system_reform")
    require(
        failures,
        regimental_flag >= 0
        and regimental_reform >= 0
        and regimental_flag < regimental_reform,
        "HET regimental unlock flag is set after the reform is granted",
    )
    academy_flag = het.find("set_country_flag = academy_expanded")
    academy_reform = het.find("add_government_reform = het_academy_enlightenment_reform")
    require(
        failures,
        academy_flag >= 0
        and academy_reform >= 0
        and academy_flag < academy_reform,
        "HET academy unlock flag is set after the reform is granted",
    )

    het_reforms = read("common/government_reforms/RIP_HET_government_reforms.txt")
    owner_change = read("common/scripted_effects/01_scripted_effects_for_on_actions.txt")
    het_migration = read("common/scripted_effects/het_effects.txt")
    het_startup = read("common/on_actions/het_on_actions.txt")
    require(
        failures,
        "het_regimental_province_administration" in het_reforms
        and "het_regimental_province_administration" in owner_change
        and "name = the_provincial_system" not in het_reforms,
        "HET regimental provinces still collide with the vanilla Ottoman pasha modifier",
    )
    require(
        failures,
        "has_reform = het_regimental_system_reform" in het_migration
        and "remove_province_modifier = the_provincial_system" in het_migration
        and "name = het_regimental_province_administration" in het_migration
        and "het_reconcile_regimental_province_modifiers_effect = yes" in het_startup,
        "old HET saves do not migrate the borrowed Ottoman province modifier",
    )
    het_break_overlord = normalized(
        named_block(het_migration, "het_break_with_overlord_effect")
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in het_break_overlord
        and "add_legitimacy = 10" not in het_break_overlord,
        "het_break_with_overlord_effect gives republican HET a legitimacy no-op",
    )
    sacred_migration = normalized(
        named_block(het_migration, "het_migrate_legacy_sacred_origin_effect")
    )
    sacred_change = sacred_migration.find("change_tag = ZAZ")
    sacred_swap = sacred_migration.find("swap_non_generic_missions = yes", sacred_change)
    sacred_on_change = sacred_migration.find("on_change_tag_effect = yes", sacred_swap)
    require(
        failures,
        "tag = HET" in sacred_migration
        and "has_country_flag = rip_hetmanate_origin_zaz" in sacred_migration
        and "has_reform = zaz_sacred_host_order_reform" in sacred_migration
        and "has_reform = zaz_sacred_horde_reform" in sacred_migration
        and "NOT = { exists = ZAZ }" in sacred_migration
        and sacred_change >= 0
        and sacred_change < sacred_swap < sacred_on_change
        and "remove_government_reform = zaz_sacred_host_order_reform" in sacred_migration
        and "remove_government_reform = zaz_sacred_horde_reform" in sacred_migration
        and "change_government = republic" in sacred_migration
        and "add_government_reform = rip_cossacks_reform" in sacred_migration
        and "het_migrate_legacy_sacred_origin_effect = yes" in het_startup,
        "old sacred-route HET saves are not migrated to a coherent government tree",
    )

    danube = normalized(
        named_block(read("missions/zzz_Hetmanate_Missions.txt"), "het_danube_frontier")
    )
    require(
        failures,
        "province_id = 159" in danube
        and "159 = { country_or_non_sovereign_subject_holds = ROOT" in danube
        and "province_id = 153" not in danube
        and "153 = {" not in danube,
        "HET Danube Frontier does not consistently target Silistria/Dobruja (159)",
    )
    ottoman_threat_raw = named_block(read("missions/Podillia_Missions.txt"), "PDL_withstand_ottoman_threat")
    ottoman_highlight = normalized(named_block(ottoman_threat_raw, "provinces_to_highlight"))
    require(
        failures,
        "area = podolia_volhynia_area" in ottoman_highlight
        and "NOT = { owned_by = ROOT" in ottoman_highlight
        and not re.search(r"\b47(?:4[9]|[5-9][0-9])\b", ottoman_highlight),
        "PDL Ottoman Threat highlights unrelated placeholder provinces",
    )
    zaz_het_triggers = read("common/scripted_triggers/zaz_het_triggers.txt")
    wild_fields = normalized(named_block(zaz_het_triggers, "is_wild_fields"))
    sloboda = normalized(named_block(zaz_het_triggers, "can_establish_sloboda"))
    require(
        failures,
        "province_id = 2410" not in wild_fields
        and "province_id = 2411" not in wild_fields
        and "area = sloboda_ukraine_area" in sloboda
        and "province_id = 2408" not in sloboda,
        "ZAZ/HET regional triggers still depend on mislabeled redundant province IDs",
    )

    union = normalized(named_block(read("events/UnionDispute.txt"), "country_event"))
    require(
        failures,
        "set_country_flag = lit_union_path_open" in union
        and "set_country_flag = lit_separate_path_open" in union,
        "LIT deferral option can still close both constitutional endpoints",
    )

    collegium_raw = named_block(read("events/HetmanateFlavor.txt"), "country_event", occurrence=12)
    collegium = normalized(collegium_raw)
    collegium_resistance = normalized(named_block(collegium_raw, "option", occurrence=2))
    require(
        failures,
        "id = het_flavor.12" in collegium
        and "government = republic" in collegium
        and "NOT = { is_year = 1728" in collegium
        and "mean_time_to_happen = { months = 24" in collegium
        and "add_republican_tradition = -10" in collegium
        and "name = het_autonomy_guaranteed" in collegium_resistance
        and "name = centralization_modifier" not in collegium_resistance,
        "Little Russian Collegium is not confined to the republican HET path or its choices contradict the narrative",
    )

    pdl_tolerance = normalized(
        named_block(
            read("common/government_reforms/RIP_PDL_government_reforms.txt"),
            "pdl_religious_tolerance_reform",
        )
    )
    require(
        failures,
        "religion = jewish" not in pdl_tolerance
        and "NOT = { religious_unity = 0.8 }" in pdl_tolerance
        and "religion = orthodox" in pdl_tolerance
        and "religion = catholic" in pdl_tolerance
        and "religion = greek_catholic" in pdl_tolerance,
        "pdl_religious_tolerance_reform AI weight still checks state religion = jewish instead of multi-confessional borderland conditions",
    )

    reform_map_doc = read("docs/GOVERNMENT_REFORMS_MAP.uk.md")
    require(
        failures,
        "`primary_culture`" in reform_map_doc
        and "accepted / dominant" not in reform_map_doc
        and "`accepted_culture` або `dominant_culture`" not in reform_map_doc,
        "docs/GOVERNMENT_REFORMS_MAP.uk.md still documents stale accepted_culture / dominant_culture unlocking for shared Ruthenian reforms",
    )

    chr_reforms_raw = read("common/government_reforms/RIP_CHR_government_reforms.txt")
    for road_a_reform in (
        "chr_desna_staple_reform",
        "chr_town_union_reform",
        "chr_rada_of_lands_reform",
    ):
        road_a_block = normalized(named_block(chr_reforms_raw, road_a_reform))
        require(
            failures,
            "chr_charter_the_staple_effect = yes" in road_a_block
            and "chr_clear_staple_charter_if_left_road_effect = yes" in road_a_block,
            f"CHR Road A reform lacks province modifier sync hooks: {road_a_reform}",
        )
    for road_b_reform in (
        "chr_magistrat_rule_reform",
        "chr_siversk_principality_reform",
        "chr_prykaz_tsardom_reform",
    ):
        road_b_block = normalized(named_block(chr_reforms_raw, road_b_reform))
        require(
            failures,
            "chr_open_the_ledger_effect = yes" in road_b_block
            and "chr_clear_house_ledger_if_left_road_effect = yes" in road_b_block,
            f"CHR Road B reform lacks province modifier sync hooks: {road_b_reform}",
        )
    chr_path_effects = normalized(read("common/scripted_effects/chr_path_effects.txt"))
    chr_on_actions = normalized(read("common/on_actions/chr_on_actions.txt"))
    chr_decisions = read("decisions/ChernihivPaths.txt")
    require(
        failures,
        "chr_reconcile_path_province_modifiers_effect = {" in chr_path_effects
        and "chr_reconcile_path_province_modifiers_effect = yes" in chr_on_actions
        and "chr_staple_charter" in owner_change
        and "chr_house_ledger" in owner_change
        and "chr_siverian_town" in owner_change
        and "chr_charter_the_staple_effect = yes"
        in normalized(named_block(chr_decisions, "chr_rada_of_all_the_lands"))
        and "chr_open_the_ledger_effect = yes"
        in normalized(named_block(chr_decisions, "chr_crown_the_prykaz_tsardom")),
        "CHR Road A/B and Great Chernihiv province modifiers are not synchronized across reform changes, conquests, or trade-good changes",
    )


def check_vanilla_overrides(failures: list[str], reforms: str) -> None:
    for reform in VANILLA_OVERRIDE_REFORMS:
        block = named_block(reforms, reform)
        require(failures, bool(block), f"missing vanilla override definition: {reform}")
        norm = normalized(block)
        require(
            failures,
            "religion = russian_orthodox" in norm,
            f"{reform} must support russian_orthodox for Muscovy/Russia compatibility",
        )


def main() -> int:
    failures: list[str] = []
    try:
        reforms, owners = reform_sources()
    except ValueError as exc:
        print(f"GOVERNMENT REFORM CHECK: FAIL\n  - {exc}")
        return 1

    mod_owners = {k: v for k, v in owners.items() if k not in VANILLA_OVERRIDE_REFORMS}
    check_vfs_and_schema(failures, reforms, mod_owners)
    check_registration(failures, mod_owners)
    check_localisation(failures, mod_owners)
    check_vanilla_overrides(failures, reforms)
    check_reachability_and_scope(failures, reforms)
    check_linked_lifecycle(failures)

    if failures:
        print("GOVERNMENT REFORM CHECK: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "GOVERNMENT REFORM CHECK: PASS "
        f"({EXPECTED_REFORM_COUNT} definitions; VFS, tiers, gates, and lifecycle hold)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
