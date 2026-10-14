# Isolated startup smoke. Uses only its own new userdir and its own process.
# This is not a campaign or a test of interactive choices.
[CmdletBinding()]
param([int]$TimeoutSeconds = 120)
$ErrorActionPreference = 'Stop'
$ripRepo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$ripGame = 'D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV'
$ripMeta = Get-Content -LiteralPath (Join-Path $ripGame 'launcher-settings.json') -Raw | ConvertFrom-Json
if ($ripMeta.rawVersion -notin @('v1.37.5.0','1.37.5.0','1.37.5')) { throw 'EU4 1.37.5 is required.' }
if (Get-Process -Name eu4 -ErrorAction SilentlyContinue) { throw 'An existing EU4 process is running; it has not been touched.' }
if ($TimeoutSeconds -lt 15 -or $TimeoutSeconds -gt 300) { throw 'Timeout must be 15..300 seconds.' }
$ripRun = Join-Path $ripRepo ('diagnostics/authenticity_runtime_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
if (Test-Path -LiteralPath $ripRun) { throw 'Run directory already exists.' }
$ripUtf8 = [Text.UTF8Encoding]::new($false)
New-Item -ItemType Directory -Path (Join-Path $ripRun 'mod') -Force | Out-Null
[IO.File]::WriteAllText((Join-Path $ripRun 'mod/RIP.mod'), (Get-Content -LiteralPath (Join-Path $ripRepo 'descriptor.mod') -Raw), $ripUtf8)
[IO.File]::WriteAllText((Join-Path $ripRun 'dlc_load.json'), '{"enabled_mods":["mod/RIP.mod"],"disabled_dlcs":[]}', $ripUtf8)
$ripSettings = @'
language="l_english"
graphics={
 adapter=0
 size={ x=1280 y=720 }
 min_gui={ x=1280 y=720 }
 refreshRate=60
 fullScreen=no
 borderless=no
 shadows=no
 multi_sampling=0
 maxanisotropy=0
 vsync=no
}
master_volume=0
music_volume=0
autosave="NEVER"
autosave_tocloud=no
compress_saves=no
graceful_exit=yes
'@
[IO.File]::WriteAllText((Join-Path $ripRun 'settings.txt'), $ripSettings, $ripUtf8)
[IO.File]::WriteAllText((Join-Path $ripRun 'rip_authenticity_setup.txt'), "debug_mode`npause`n", $ripUtf8)
function Get-RipSourceManifest {
    $ripRows = @()
    foreach ($ripFolder in @('common','customizable_localization','decisions','events','gfx','history','interface','localisation','map','missions','sound')) {
        $ripPath = Join-Path $ripRepo $ripFolder
        if (Test-Path -LiteralPath $ripPath) {
            foreach ($ripFile in Get-ChildItem -LiteralPath $ripPath -File -Recurse | Sort-Object FullName) {
                $ripRows += [ordered]@{path=$ripFile.FullName.Substring($ripRepo.Length+1).Replace('\','/');sha256=(Get-FileHash -LiteralPath $ripFile.FullName -Algorithm SHA256).Hash}
            }
        }
    }
    $ripRows += [ordered]@{path='descriptor.mod';sha256=(Get-FileHash -LiteralPath (Join-Path $ripRepo 'descriptor.mod') -Algorithm SHA256).Hash}
    return $ripRows
}
$ripSource = @(Get-RipSourceManifest)
$ripArguments = @('-debug_mode','-start_tag=MOS','-seed=1001',('-userdir="' + $ripRun + '"'),'-auto_run=rip_authenticity_setup.txt')
$ripManifest = [ordered]@{
    started_utc=[DateTime]::UtcNow.ToString('o'); game_version=$ripMeta.rawVersion
    executable=(Join-Path $ripGame 'eu4.exe'); arguments=$ripArguments; userdir=$ripRun
    git_head=(& git -C $ripRepo rev-parse HEAD); source_sha256=$ripSource
    status='prepared'; startup_pass=$false; branch_execution='not_tested'; campaign_balance='not_tested'
}
$ripManifestPath = Join-Path $ripRun 'manifest.json'
[IO.File]::WriteAllText($ripManifestPath, ($ripManifest | ConvertTo-Json -Depth 7), $ripUtf8)
$ripProcess = Start-Process -FilePath (Join-Path $ripGame 'eu4.exe') -WorkingDirectory $ripGame -ArgumentList $ripArguments -WindowStyle Hidden -PassThru
$ripManifest.pid = $ripProcess.Id
$ripManifest.status = 'running'
[IO.File]::WriteAllText($ripManifestPath, ($ripManifest | ConvertTo-Json -Depth 7), $ripUtf8)
Write-Output "Started isolated EU4 PID $($ripProcess.Id). Evidence: $ripRun"
$ripTimer = [Diagnostics.Stopwatch]::StartNew()
while (-not $ripProcess.HasExited -and $ripTimer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
    Start-Sleep -Seconds 2
    $ripProcess.Refresh()
}
if (-not $ripProcess.HasExited) {
    Stop-Process -Id $ripProcess.Id -Force
    $ripManifest.status = 'stopped_own_process_at_timeout'
} else {
    $ripManifest.status = 'process_exited'
    $ripManifest.exit_code = $ripProcess.ExitCode
}
$ripManifest.ended_utc = [DateTime]::UtcNow.ToString('o')
$ripAfter = @(Get-RipSourceManifest)
$ripManifest.source_unchanged = (($ripSource | ConvertTo-Json -Depth 3 -Compress) -eq ($ripAfter | ConvertTo-Json -Depth 3 -Compress))
$ripLogs = @()
foreach ($ripLog in Get-ChildItem -LiteralPath (Join-Path $ripRun 'logs') -File -ErrorAction SilentlyContinue) {
    $ripLogs += [IO.File]::ReadAllText($ripLog.FullName)
}
if (($ripLogs -join "`n") -match '(?i)(failed.*(d3d|direct3d)|failed to create.*device)') {
    $ripManifest.status = 'blocked_before_content_load_d3d_device_failure'
}
[IO.File]::WriteAllText($ripManifestPath, ($ripManifest | ConvertTo-Json -Depth 7), $ripUtf8)
Write-Output "Status: $($ripManifest.status); source unchanged: $($ripManifest.source_unchanged). Inspect full logs before declaring startup success."
