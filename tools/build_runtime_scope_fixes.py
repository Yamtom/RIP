"""Minimal full-file vanilla overrides for EU4 1.37; --check never writes.

Keep the entire native files: on_actions are additive across distinct filenames.
Reject changed upstream patterns rather than silently generating an unpatched file.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from clausewitz_testlib import ROOT, vanilla_root


def outputs(game):
    path = 'common/new_diplomatic_actions/00_diplomatic_actions.txt'
    text = (game / path).read_text(encoding='utf-8-sig')
    old = 'value = num_of_loans'
    assert text.count(old) == 2, 'Re-audit native loan exports after game update'
    # SIZE_OF_LOANS concerns the recipient, just like its FROM loan trigger.
    text = text.replace(old, 'value = trigger_value:num_of_loans\n\t\t\t\twho = FROM')
    yield path, text

    path = 'common/on_actions/00_on_actions.txt'
    text = (game / path).read_text(encoding='utf-8-sig')
    old = 'FROM = { economic_ideas = 3 }'
    assert text.count(old) == 1, 'Re-audit native trade-good hook after game update'
    # Trade-good setup may have no originating country; use the province owner.
    text = text.replace(old, 'owner = { economic_ideas = 3 }')
    yield path, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    game = vanilla_root()
    if game is None:
        parser.error('Installed EU4 1.37 source is required')
    changed = []
    for relative, text in outputs(game):
        target = ROOT / relative
        if not target.exists() or target.read_text(encoding='utf-8') != text:
            changed.append(relative)
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding='utf-8', newline='\n')
    print(('STALE' if args.check and changed else 'PASS') + ': runtime scope overrides; ' + str(len(changed)) + ' changed')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())
