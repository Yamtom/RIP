# Build and run the faith balance simulations.
#
# There is no compiler on PATH on this machine - `Get-Command g++/clang++/cl`
# finds nothing - but MSVC 2022 Community is installed, and cl.exe works once
# vcvars64.bat has set the environment. That is the whole reason this wrapper
# exists rather than a plain `cl` invocation.
#
#   powershell -File tests/dev_tools/balance_sim/build_and_run.ps1

$ErrorActionPreference = 'Stop'
$here  = Split-Path -Parent $MyInvocation.MyCommand.Path
$build = Join-Path $here 'build'

$vcvars = @(
    'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat'
    'C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat'
    'C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat'
    'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $vcvars) {
    Write-Host 'No MSVC found. Install Visual Studio 2022 (or the Build Tools),'
    Write-Host 'or compile by hand with any C++17 compiler:'
    Write-Host '    g++ -std=c++17 -O2 faith_sim.cpp -o faith_sim'
    exit 1
}

if (-not (Test-Path $build)) { New-Item -ItemType Directory $build | Out-Null }

foreach ($name in @('faith_sim', 'icon_sim')) {
    $src = Join-Path $here "$name.cpp"
    $exe = Join-Path $build "$name.exe"
    Write-Host ""
    Write-Host "=== $name ===" -ForegroundColor Cyan

    # /Fo and /Fe keep the .obj and .exe out of the source directory
    $cmd = '"' + $vcvars + '" >nul 2>&1 && cl /nologo /std:c++17 /EHsc /O2 "' + $src +
           '" /Fo"' + $build + '\\" /Fe"' + $exe + '" >nul'
    cmd /c $cmd
    if ($LASTEXITCODE -ne 0) { Write-Host "compile failed: $name"; exit 1 }

    cmd /c "`"$exe`""
    if ($LASTEXITCODE -ne 0) { Write-Host "run failed: $name"; exit 1 }
}

Write-Host ""
Write-Host 'Both simulations ran. Compare the numbers against the tables in README.md;' -ForegroundColor Green
Write-Host 'if they have drifted, the script and the models disagree - fix both together.' -ForegroundColor Green
