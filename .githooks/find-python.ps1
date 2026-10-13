# Discovery only: never install software or change the repository/environment.
$ErrorActionPreference = 'SilentlyContinue'
$candidates = @(
    [Environment]::GetEnvironmentVariable('RIP_PYTHON', 'User')
    [Environment]::GetEnvironmentVariable('RIP_PYTHON', 'Machine')
)
$launcher = Get-Command py.exe -CommandType Application -ErrorAction SilentlyContinue
if ($launcher) {
    $candidates += & $launcher.Source -3 -B -c 'import sys; print(sys.executable)' 2>$null
}
foreach ($base in @("$env:LOCALAPPDATA/Programs/Python", "$env:ProgramFiles", 'C:/')) {
    $candidates += Get-ChildItem -LiteralPath $base -Directory -Filter 'Python*' |
        ForEach-Object { Join-Path $_.FullName 'python.exe' }
}
# Existing bundled Python is preferable to downloading another interpreter.
$candidates += "$env:ProgramFiles/NVIDIA Corporation/RTX Remix/kit/python/python.exe"
foreach ($candidate in $candidates) {
    if (-not $candidate -or $candidate -match 'WindowsApps' -or
        -not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
    $LASTEXITCODE = -1
    & $candidate -B -c 'import sys; assert sys.version_info >= (3, 10)' *> $null
    if ($LASTEXITCODE -eq 0) {
        [Console]::Write($candidate)
        exit 0
    }
}
exit 1
