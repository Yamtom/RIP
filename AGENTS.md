# RIP: mandatory encoding gate

Before editing engine files and before reporting completion, run
`python -B tests/check_file_encoding.py` and
`python -B tests/check_clausewitz_braces.py` with a real Python 3.10+ interpreter.
Fix encoding failures before launch or commit. Static checks do not prove runtime.

EU4 `.txt`, `.gui`, `.gfx` and `.mod` engine files must be UTF-8 **without BOM**.
`localisation/**/*.yml` must be UTF-8 **with exactly one BOM**.
Do not use default Windows PowerShell `Out-File`/`Set-Content` encodings.
Edit generators first, regenerate, then repeat both checks.

This checkout uses `.githooks/pre-commit`, which checks staged BOM bytes and
engine syntax. Enable it in a fresh clone with
`git config --local core.hooksPath .githooks`.
Set `RIP_PYTHON` to a real Python executable if it is not on PATH.
