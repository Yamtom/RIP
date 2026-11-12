"""Export reviewed monument PNG masters to EU4 DDS; requires Pillow.

python -B tools/build_great_project_art.py [--check]
Only resizes and converts approved artwork; no procedural scene generation.
"""
from pathlib import Path
import argparse
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'gfx/interface/great_projects'
NAMES = ('vilnius_palace', 'palanok_fortress', 'zaporozhian_sich')


def render(name: str) -> Image.Image:
    if name not in NAMES:
        raise ValueError(name)
    with Image.open(ART / 'source' / (name + '_reference.png')) as master:
        if master.width != 2 * master.height:
            raise ValueError(f'{name}: master must have 2:1 aspect ratio')
        return master.convert('RGBA').resize((300, 150), Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name in NAMES:
        expected = render(name)
        suffix = '_reference' if name == 'zaporozhian_sich' else ''
        target = ART / ('great_project_' + name + suffix + '.dds')
        if not args.check:
            unchanged = False
            if target.exists():
                with Image.open(target) as existing:
                    unchanged = (existing.size == expected.size and
                                 existing.convert('RGBA').tobytes() == expected.tobytes())
            if not unchanged:
                expected.save(target, format='DDS')
        with Image.open(target) as actual:
            assert actual.size == (300, 150), target
            assert actual.convert('RGBA').tobytes() == expected.tobytes(), target
        raw = target.read_bytes()
        assert raw[:4] == b'DDS ' and len(raw) == 180128, target
        assert raw[84:88] == b'\0' * 4, target
        matches = []
        for path in (ROOT / 'interface').glob('*.gfx'):
            text = path.read_text(encoding='utf-8-sig')
            matches.extend(re.findall(
                r'spriteType\s*=\s*\{\s*name\s*=\s*"GFX_great_project_'
                + name + r'"\s*texturefile\s*=\s*"([^"]+)"', text))
        assert len(matches) == 1, (name, matches)
        assert ROOT.joinpath(matches[0].replace('//', '/')).resolve() == target.resolve()
        print('PASS:', name, '300x150 BGRA DDS, master pixels, unique sprite/path')


if __name__ == '__main__':
    main()
