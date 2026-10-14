"""Regression cases for the BOM policy and staged-byte enforcement."""
import contextlib
import io
import sys
from unittest.mock import patch

import check_file_encoding as guard


def main():
    for path in ("descriptor.mod", ".githooks/pre-commit", "interface/a.gui", "interface/a.gfx", "common/a.txt",
                 "events/a.txt", "history/a.txt", "customizable_localization/a.txt"):
        assert guard.error(path, b"name = ok") is None
        assert guard.error(path, guard.BOM + b"name = ok")
        assert guard.error(path, b"\xff\xfeN\x00")
    assert guard.error("localisation/replace/a.yml", guard.BOM + b"l_english:\n") is None
    assert guard.error("localisation/a.yml", b"l_english:\n")
    assert guard.error("localisation/a.yml", guard.BOM * 2 + b"l_english:\n")
    assert guard.error(".githooks/pre-commit", b"#!/bin/sh\r\nset -eu\r\n")
    assert guard.error("docs/a.md", guard.BOM + b"documentation") is None
    assert guard.error("diagnostics/old/descriptor.mod", guard.BOM + b"name = old") is None
    assert guard.error(".claude/worktrees/old/descriptor.mod", guard.BOM + b"name = old") is None
    calls = []
    def staged(*args):
        calls.append(args)
        return b"interface/space name.gui\0" if args[0] == "diff" else guard.BOM + b"guiTypes = {}"
    with patch.object(sys, "argv", ["check_file_encoding.py", "--staged"]), \
            patch.object(guard, "git_bytes", staged), contextlib.redirect_stdout(io.StringIO()):
        assert guard.main() == 1
    assert ("show", ":interface/space name.gui") in calls
    print("ENCODING GUARD PASS: descriptor/data/localisation policy and staged-byte rejection")


if __name__ == "__main__":
    main()
