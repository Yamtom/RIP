param(
    [string]$EvidenceDirectory = (Join-Path $PWD 'diagnostics/church_ux_20261002'),
    [string]$RunName = 'rip-church-ux-20261002'
)
$ErrorActionPreference = 'Stop'
$ripRepo = [IO.Path]::GetFullPath((Join-Path $EvidenceDirectory '../..'))
if ($RunName -notmatch '^rip-church-ux-[0-9a-z-]+$') { throw 'Invalid QA directory name.' }
$ripRun = Join-Path $env:TEMP $RunName
if (Get-Process -Name eu4 -ErrorAction SilentlyContinue) { throw 'Existing EU4 process; leave it untouched.' }
if (Test-Path -LiteralPath $ripRun) { throw 'QA directory already exists; use another name.' }
$ripSource = Join-Path $ripRun 'source'
$ripProfile = Join-Path $ripRun 'profile'
$ripUtf8 = [Text.UTF8Encoding]::new($false)
New-Item -ItemType Directory -Path $ripSource,(Join-Path $ripProfile 'mod') -Force | Out-Null
$ripPaths = @(& git ls-files --cached --others --exclude-standard -- common customizable_localization decisions events gfx history interface localisation map missions sound descriptor.mod | Sort-Object -Unique)
$ripInventory = @()
foreach ($ripPath in $ripPaths) {
    $ripOriginal = Join-Path $ripRepo $ripPath
    $ripCopy = Join-Path $ripSource $ripPath
    New-Item -ItemType Directory -Path (Split-Path -Parent $ripCopy) -Force | Out-Null
    Copy-Item -LiteralPath $ripOriginal -Destination $ripCopy
    $ripInventory += [ordered]@{path=$ripPath;sha256=(Get-FileHash -LiteralPath $ripOriginal -Algorithm SHA256).Hash}
}
# Fixtures are applied only to this immutable QA copy.
$ripPrior = Join-Path $env:TEMP 'rip-gui-static-values-20261002/source'
$ripFixtures = @()
foreach ($ripPath in @('history/countries/POL - Poland.txt','history/provinces/262 - Krakow.txt','history/provinces/259 - Sandomierz.txt')) {
    Copy-Item -LiteralPath (Join-Path $ripPrior $ripPath) -Destination (Join-Path $ripSource $ripPath)
    $ripFixtures += [ordered]@{path=$ripPath;sha256=(Get-FileHash -LiteralPath (Join-Path $ripSource $ripPath) -Algorithm SHA256).Hash;change='GC Poland; one Eastern and one Latin recognized province'}
}
$ripFixturePath = 'common/on_actions/zzz_rip_gui_ux_qa_on_actions.txt'
$ripFixture = @'
# QA only: native effects in country on_startup scope.
on_startup = {
 if = {
  limit = { tag = POL }
  add_patriarch_authority = 1
  add_treasury = 300
  rip_church_refresh_pa_effect = yes
  rip_church_gc_refresh_parishes_effect = yes
 }
}
'@
[IO.File]::WriteAllText((Join-Path $ripSource $ripFixturePath),$ripFixture,$ripUtf8)
$ripFixtures += [ordered]@{path=$ripFixturePath;sha256=(Get-FileHash -LiteralPath (Join-Path $ripSource $ripFixturePath) -Algorithm SHA256).Hash;change='QA Poland HC 100 and +300 ducats'}
$ripDescriptor = 'name="RIP church UX QA"' + "`n" + 'path="' + $ripSource.Replace('\','/') + '"' + "`n" + 'supported_version="1.37.*"' + "`n"
[IO.File]::WriteAllText((Join-Path $ripProfile 'mod/rip_gui_qa.mod'),$ripDescriptor,$ripUtf8)
[IO.File]::WriteAllText((Join-Path $ripProfile 'dlc_load.json'),'{"enabled_mods":["mod/rip_gui_qa.mod"],"disabled_dlcs":[]}',$ripUtf8)
Copy-Item -LiteralPath (Join-Path $env:TEMP 'rip-gui-static-values-20261002/profile/settings.txt') -Destination (Join-Path $ripProfile 'settings.txt')
$ripArguments = @('-debug_mode','-start_tag=POL','-seed=1001',('-userdir="' + $ripProfile + '"'))
$ripManifest = [ordered]@{
    status='prepared';game_version='1.37.5';git_head=(& git rev-parse HEAD)
    executable='D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV\eu4.exe'
    arguments=$ripArguments;profile=$ripProfile;source=$ripSource;source_files=$ripInventory.Count
    fixtures=$ripFixtures;patch_state=(& git status --short);source_sha256=$ripInventory
}
[IO.File]::WriteAllText((Join-Path $ripRun 'run.json'),($ripManifest | ConvertTo-Json -Depth 6),$ripUtf8)
[IO.File]::WriteAllText((Join-Path $EvidenceDirectory 'source_sha256.json'),($ripInventory | ConvertTo-Json -Depth 3),$ripUtf8)
Write-Output "Prepared $($ripInventory.Count) files, including new DDS icons, in $ripRun"
