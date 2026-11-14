# Compatibility entry point; Pillow owns the reproducible DDS recipe.
param([switch]$Check)
$builder = Join-Path $PSScriptRoot 'build_ro_banner_textures.py'
$interpreter = if ($env:RIP_PYTHON) { $env:RIP_PYTHON } else { 'python' }
if ($Check) { & $interpreter -B $builder --check }
else { & $interpreter -B $builder }
exit $LASTEXITCODE
