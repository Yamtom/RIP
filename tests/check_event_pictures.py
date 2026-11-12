"""Verify event-picture links, generated DDS textures, and the shared legacy sprite."""

from __future__ import annotations

import re
import struct
import sys

from clausewitz_testlib import ROOT, keyed_blocks, read


SPRITE_TEXTURES = {
    "rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_eventPicture.dds",
    "rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_art_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_art_eventPicture.dds",
    "rip_gfx_event_south_ukraine_imperial_frontier_reform_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_south_ukraine_imperial_frontier_reform_art_eventPicture.dds",
    "rip_gfx_event_hetmanate_little_russian_collegium_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_hetmanate_little_russian_collegium_art_eventPicture.dds",
    "rip_gfx_event_kyiv_orthodox_printing_press_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_kyiv_orthodox_printing_press_art_eventPicture.dds",
    "rip_gfx_event_jewish_estate_invite_merchants_eventPicture":
        "gfx/event_pictures/event_pictures_rip/rip_gfx_event_jewish_estate_invite_merchants_art_eventPicture.dds",
}

SCALAR_EVENTS = (
    (
        "events/RIP_shared_steppe_SouthUkraineHistorical.txt",
        "south_ukraine_history.7",
        "rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_art_eventPicture",
    ),
    (
        "events/RIP_shared_ruthenian_KyivDnieperHistorical.txt",
        "kyiv_dnieper_history.10",
        "rip_gfx_event_kyiv_orthodox_printing_press_eventPicture",
    ),
    (
        "events/RIP_shared_estates_JewishEstate.txt",
        "rip_jewish.1",
        "rip_gfx_event_jewish_estate_invite_merchants_eventPicture",
    ),
    (
        "events/RIP_shared_estates_JewishEstate.txt",
        "rip_jewish.99",
        "rip_gfx_event_jewish_estate_invite_merchants_eventPicture",
    ),
    (
        "events/RIP_shared_steppe_SouthUkraineHistorical.txt",
        "south_ukraine_history.12",
        "rip_gfx_event_south_ukraine_imperial_frontier_reform_eventPicture",
    ),
    (
        "events/RIP_HET_HetmanateFlavor.txt",
        "het_flavor.12",
        "rip_gfx_event_hetmanate_little_russian_collegium_eventPicture",
    ),
    (
        "events/RIP_shared_orthodox_RussianOrthodox.txt",
        "russian_orthodox.17",
        "rip_gfx_event_south_ukraine_zaporozhian_autonomy_charter_eventPicture",
    ),
)


def event_block(relative: str, event_id: str) -> str:
    event_id_pattern = re.compile(rf"(?m)^\s*id\s*=\s*{re.escape(event_id)}\s*$")
    matches = [
        block for _, block in keyed_blocks(read(relative), "country_event")
        if event_id_pattern.search(block) and re.search(r"(?m)^\s*title\s*=", block)
    ]
    if len(matches) != 1:
        raise ValueError(f"{relative}: expected one event {event_id}, found {len(matches)}")
    return matches[0]


def scalar_picture(text: str) -> str:
    pictures = re.findall(r"(?m)^\s*picture\s*=\s*([A-Za-z_][A-Za-z_0-9]*)\s*$", text)
    if len(pictures) != 1:
        raise ValueError(f"expected one picture scalar, found {pictures}")
    return pictures[0]


def check_event_pictures(failures: list[str]) -> None:
    for relative, event_id, expected in SCALAR_EVENTS:
        try:
            event = event_block(relative, event_id)
            if list(keyed_blocks(event, "picture")):
                raise ValueError("a conditional picture may override the original art")
            actual = scalar_picture(event)
            if actual != expected:
                failures.append(f"{event_id}: expected {expected}, found {actual}")
        except ValueError as exc:
            failures.append(f"{event_id}: {exc}")


def check_sprite_textures(failures: list[str]) -> None:
    definitions: dict[str, list[str]] = {name: [] for name in SPRITE_TEXTURES}
    for gfx in (ROOT / "interface").glob("*.gfx"):
        for _, block in keyed_blocks(gfx.read_text(encoding="utf-8-sig"), "spriteType"):
            name = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', block)
            if name and name.group(1) in definitions:
                texture = re.search(r'(?m)^\s*texturefile\s*=\s*"([^"]+)"', block)
                definitions[name.group(1)].append(texture.group(1) if texture else "<missing>")

    for name, expected in SPRITE_TEXTURES.items():
        if definitions[name] != [expected]:
            failures.append(f"{name}: expected texture {expected}, found {definitions[name]}")

    for relative in SPRITE_TEXTURES.values():
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing texture: {path}")
            continue
        data = path.read_bytes()
        if len(data) < 128 or data[:4] != b"DDS ":
            failures.append(f"invalid DDS header: {path}")
        elif struct.unpack_from("<II", data, 12) != (132, 512):
            failures.append(f"expected a 512x132 DDS: {path}")
        elif relative.endswith("_art_eventPicture.dds"):
            if (
                len(data) != 128 + 512 * 132 * 4
                or data[84:88] != b"\0\0\0\0"
                or struct.unpack_from("<I", data, 88)[0] != 32
                or struct.unpack_from("<I", data, 104)[0] != 0xFF000000
            ):
                failures.append(f"expected a complete 32-bit legacy DDS: {path}")
            elif any(alpha != 255 for alpha in data[131::4]):
                failures.append(f"event picture must be opaque: {path}")


def main() -> int:
    failures: list[str] = []
    check_event_pictures(failures)
    check_sprite_textures(failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Event pictures: five original DDS links and the shared legacy sprite verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
