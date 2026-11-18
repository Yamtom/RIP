"""Static historical-geography and mechanics contracts for UZH (no runtime claim)."""
from __future__ import annotations

import re

from clausewitz_testlib import ROOT, named_block, normalized, read


MODIFIED_LOC_KEYS = (
    "uzh.203.t",
    "uzh.203.d",
    "uzh.203.b",
    "uz_coal_foundry_network",
    "desc_uz_coal_foundry_network",
    "uz_coal_export_charters",
    "desc_uz_coal_export_charters",
    "UZH_industrial_coal_tt",
    "uz_preserve_orthodox_faith_desc",
    "uz_mukachevo_autonomy_desc",
    "uz_kyivan_heritage_desc",
    "ZAKARPATTIA_HISTORICAL_OVERVIEW",
    "uzh_danube_trade_league_desc",
    "uzh.410.d",
    "uzh.410.a",
    "uzh_raise_serdyuk_host_title",
    "uzh_raise_serdyuk_host_desc",
    "uz_serdyuk_guard",
    "desc_uz_serdyuk_guard",
    "uzh_tisza_customs_convention_desc",
    "UZH_tisza_customs_downstream_tt",
    "uzh.242.d",
)


def loc_entries(path) -> dict[str, str]:
    return dict(
        re.findall(
            r'^ ([A-Za-z0-9_.\-]+):\d+ "(.*)"$',
            path.read_text(encoding="utf-8-sig"),
            re.M,
        )
    )


def main() -> int:
    missions = read("missions/Zakarpatta_Missions.txt")
    reforms = read("common/government_reforms/RIP_UZH_government_reforms.txt")
    country_hist = read("history/countries/UZH - Huszt.txt")
    en = loc_entries(ROOT / "localisation/RIP_UZH_realm_l_english.yml")

    # 1. Carpathian ironworks / neighboring coalfields instead of Maramaros coal seams
    ind_raw = named_block(missions, "uzh_industrial_revolution")
    ind = normalized(ind_raw)
    assert "tooltip = UZH_industrial_coal_tt" in ind_raw
    assert "trade_goods = coal value = 1" in ind
    assert (
        "region = carpathia_region OR = { trade_goods = iron trade_goods = copper "
        "trade_goods = salt trade_goods = naval_supplies } has_manufactory_trigger = yes value = 2"
        in ind
    ), "uzh_industrial_revolution must accept 2 Carpathian raw-goods manufactories as alternative to coal"
    for phrase in ("rich seams beneath the valleys", "Zakarpattian Coal", "Zakarpattian coal"):
        assert phrase not in en["uzh.203.t"] + en["uzh.203.d"] + en["desc_uz_coal_export_charters"]
    assert "iron" in en["uzh.203.d"].lower()
    assert "Dovhe" in en["uzh.203.d"] and "Kobyletska Polyana" in en["uzh.203.d"]
    for coal_hub in ("Hunyad", "Somogy", "Lviv"):
        assert coal_hub in en["uzh.203.d"] and coal_hub in en["UZH_industrial_coal_tt"]

    # 2. 1444 Koriatovych divergence and elective heir = no consistency
    captaincy = normalized(named_block(reforms, "uzh_palanok_captaincy_reform"))
    assert "heir = no" in captaincy
    hist_code = normalized(country_hist)
    assert "dynasty = Koriatovych" in hist_code
    assert "Koriyatovych" not in country_hist
    assert "heir =" not in hist_code, "UZH - Huszt.txt must not define a hereditary heir under heir = no reform"
    assert "1414" in country_hist and "Brankovic" in country_hist
    for key in ("uz_preserve_orthodox_faith_desc", "uz_mukachevo_autonomy_desc", "uz_kyivan_heritage_desc"):
        assert "1414" in en[key] and "collateral" in en[key], key
    for key in ("uz_preserve_orthodox_faith_desc", "uz_mukachevo_autonomy_desc"):
        assert "Brankovic" in en[key] and "Hunyadi" in en[key], key
    assert "Koriatovych" in en["ZAKARPATTIA_HISTORICAL_OVERVIEW"]

    # 3. Petrovaradin instead of Novi Sad; Carpathian Hajduks instead of Dnieper Serdyuks
    assert "novi sad" not in missions.lower()
    assert "novi sad" not in en["uzh_danube_trade_league_desc"].lower()
    assert "Petrovaradin" in en["uzh_danube_trade_league_desc"]
    for key in (
        "uzh.410.t",
        "uzh.410.d",
        "uzh.410.a",
        "uzh_raise_serdyuk_host_title",
        "uzh_raise_serdyuk_host_desc",
        "uz_serdyuk_guard",
        "desc_uz_serdyuk_guard",
    ):
        assert "serdyuk" not in en[key].lower(), f"stale Serdyuk wording in {key}"
    for key in (
        "uzh.410.d",
        "uzh.410.a",
        "uzh_raise_serdyuk_host_title",
        "uzh_raise_serdyuk_host_desc",
        "uz_serdyuk_guard",
        "desc_uz_serdyuk_guard",
    ):
        assert "Hajduk" in en[key], f"missing Hajduk wording in {key}"

    # 4. Tisza Customs downstream nodes: Wien (134) / Krakow (262), not upstream Ragusa (137)
    tisza = normalized(named_block(missions, "uzh_tisza_customs_convention"))
    assert "153 = { is_strongest_trade_power = ROOT }" in tisza
    assert "134 = { is_strongest_trade_power = ROOT }" in tisza
    assert "262 = { is_strongest_trade_power = ROOT }" in tisza
    assert not re.search(r"\b137\b", tisza), "137 (Ragusa) is upstream of Pest and must not be checked"
    for key in ("uzh_tisza_customs_convention_desc", "UZH_tisza_customs_downstream_tt", "uzh.242.d"):
        assert "ragusa" not in en[key].lower(), key
        assert "Wien" in en[key] and "Kraków" in en[key], key

    # 5. Replace fallback files mirror every updated English string
    for lang in ("french", "german", "spanish"):
        fallback = loc_entries(ROOT / f"localisation/replace/RIP_UZH_content_l_{lang}.yml")
        for key in MODIFIED_LOC_KEYS:
            assert fallback.get(key) == en[key], (lang, key)

    print("PASS: UZH historical geography contracts (ironworks/coal, Koriatovych 1444, Petrovaradin/Hajduk, Wien/Krakow downstream, 4 languages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
