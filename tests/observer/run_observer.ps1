#requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$Launch,

    [switch]$Smoke,

    [int[]]$Seeds = (1001..1010),

    [string]$GameExe = 'D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV\eu4.exe',

    [string]$UserDataRoot = '',

    [string]$OutputRoot = '',

    [ValidateSet('AutoRun', 'ManualConsole')]
    [string]$BootstrapMode = 'AutoRun',

    [switch]$NoGui,

    [ValidateRange(5, 60)]
    [int]$PollSeconds = 10,

    [ValidateRange(1, 1440)]
    [int]$TimeoutMinutes = 180,

    [switch]$AllowDirty,

    [switch]$ForceStopAfterCompletion
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$CommandFileVirtualPath = $(
    if ($Smoke) { 'tests/observer/commands/smoke_setup.txt' }
    else { 'tests/observer/commands/setup.txt' }
)
$TargetYear = $(if ($Smoke) { 1446 } else { 1650 })
$RequiredCheckpointYears = $(if ($Smoke) { @(1446) } else { @(1500, 1550, 1600, 1650) })

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Assert-OutputRootIsSafe {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$CandidateRoot
    )

    $repo = Get-NormalizedPath -Path $RepositoryRoot
    $candidate = Get-NormalizedPath -Path $CandidateRoot
    $repoPrefix = $repo + [System.IO.Path]::DirectorySeparatorChar

    if ($candidate.Equals($repo, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'OutputRoot must be a child directory, not the repository root itself.'
    }

    if (-not $candidate.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe OutputRoot outside repository: $candidate"
    }

    return $candidate
}

function Get-GitState {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        throw 'git is required to record the exact tested revision.'
    }

    $headLines = @(& git -C $RepositoryRoot rev-parse HEAD 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Git HEAD: $($headLines -join [Environment]::NewLine)"
    }

    $statusLines = @(& git -C $RepositoryRoot status --porcelain=v1 --untracked-files=all 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Git status: $($statusLines -join [Environment]::NewLine)"
    }

    return [pscustomobject]@{
        Head        = ([string]$headLines[0]).Trim()
        Dirty       = ($statusLines.Count -gt 0)
        StatusLines = @($statusLines | ForEach-Object { [string]$_ })
    }
}

function Get-DescriptorValue {
    param(
        [Parameter(Mandatory = $true)][string]$DescriptorPath,
        [Parameter(Mandatory = $true)][string]$Key
    )

    $content = Get-Content -LiteralPath $DescriptorPath -Raw
    $pattern = '(?m)^' + [regex]::Escape($Key) + '="([^"]+)"\s*$'
    $match = [regex]::Match($content, $pattern)
    if (-not $match.Success) {
        throw "Missing $Key in descriptor: $DescriptorPath"
    }

    return $match.Groups[1].Value
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 10
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $encoding)
}

function Get-SourceFiles {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $includedDirectories = @(
        'common',
        'customizable_localization',
        'decisions',
        'events',
        'gfx',
        'history',
        'interface',
        'localisation',
        'map',
        'missions',
        'music',
        'sound'
    )
    $includedFiles = @('descriptor.mod', 'thumbnail.png')
    $files = @()
    foreach ($directoryName in $includedDirectories) {
        $directory = Join-Path $RepositoryRoot $directoryName
        if (Test-Path -LiteralPath $directory -PathType Container) {
            $files += @(Get-ChildItem -LiteralPath $directory -Recurse -File -Force)
        }
    }
    foreach ($fileName in $includedFiles) {
        $file = Join-Path $RepositoryRoot $fileName
        if (Test-Path -LiteralPath $file -PathType Leaf) {
            $files += Get-Item -LiteralPath $file
        }
    }
    return @($files | Sort-Object FullName)
}

function Get-SourceInventory {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $rootPrefixLength = $RepositoryRoot.Length + 1
    $inventory = @()
    foreach ($file in Get-SourceFiles -RepositoryRoot $RepositoryRoot) {
        $inventory += [pscustomobject]@{
            path   = $file.FullName.Substring($rootPrefixLength).Replace('\', '/')
            length = $file.Length
            sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        }
    }
    return $inventory
}

function Get-InventoryFingerprint {
    param([Parameter(Mandatory = $true)][object[]]$Inventory)

    $lines = @($Inventory | ForEach-Object {
        '{0} {1} {2}' -f $_.sha256, $_.length, $_.path
    })
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($lines -join "`n") + "`n")
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '')
    }
    finally {
        $hasher.Dispose()
    }
}

function New-SourceSnapshot {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$SnapshotRoot,
        [Parameter(Mandatory = $true)][string]$InventoryPath
    )

    if (Test-Path -LiteralPath $SnapshotRoot) {
        throw "Refusing to reuse source snapshot directory: $SnapshotRoot"
    }
    New-Item -ItemType Directory -Path $SnapshotRoot | Out-Null

    $inventory = @(Get-SourceInventory -RepositoryRoot $RepositoryRoot)
    foreach ($item in $inventory) {
        $source = Join-Path $RepositoryRoot ($item.path -replace '/', '\')
        $destination = Join-Path $SnapshotRoot ($item.path -replace '/', '\')
        $destinationParent = Split-Path -Parent $destination
        if (-not (Test-Path -LiteralPath $destinationParent -PathType Container)) {
            New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        }
        Copy-Item -LiteralPath $source -Destination $destination
    }
    Write-JsonFile -Path $InventoryPath -Value ([pscustomobject]@{
        generated_at_utc = [DateTime]::UtcNow.ToString('o')
        files            = $inventory
    })

    return [pscustomobject]@{
        Root        = $SnapshotRoot
        Inventory   = $InventoryPath
        Fingerprint = Get-InventoryFingerprint -Inventory $inventory
        FileCount   = $inventory.Count
    }
}

function Get-Eu4SaveMetadata {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        $stream = [System.IO.File]::Open(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::ReadWrite
        )
        try {
            $reader = [System.IO.StreamReader]::new($stream)
            try {
                $firstLine = $reader.ReadLine()
                if ($firstLine -ne 'EU4txt') {
                    return $null
                }

                for ($lineNumber = 0; $lineNumber -lt 120 -and -not $reader.EndOfStream; $lineNumber++) {
                    $line = $reader.ReadLine()
                    $match = [regex]::Match($line, '^date=(\d+)\.(\d+)\.(\d+)$')
                    if ($match.Success) {
                        $year = [int]$match.Groups[1].Value
                        $month = [int]$match.Groups[2].Value
                        $day = [int]$match.Groups[3].Value
                        return [pscustomobject]@{
                            Path     = $Path
                            Name     = [System.IO.Path]::GetFileName($Path)
                            DateText = "$year.$month.$day"
                            Year     = $year
                            SortKey  = (($year * 10000) + ($month * 100) + $day)
                        }
                    }
                }
            }
            finally {
                $reader.Dispose()
            }
        }
        finally {
            $stream.Dispose()
        }
    }
    catch [System.IO.IOException] {
        return $null
    }

    return $null
}

function Wait-FileStable {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [ValidateRange(5, 120)][int]$TimeoutSeconds = 60
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $previousSignature = $null
    $stableObservations = 0

    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $file = Get-Item -LiteralPath $Path
            $signature = '{0}:{1}' -f $file.Length, $file.LastWriteTimeUtc.Ticks
            if ($file.Length -gt 0 -and $signature -eq $previousSignature) {
                $stableObservations++
                if ($stableObservations -ge 2) {
                    return
                }
            }
            else {
                $stableObservations = 0
                $previousSignature = $signature
            }
        }
        catch [System.IO.IOException] {
            $stableObservations = 0
        }

        Start-Sleep -Seconds 2
    }

    throw "Save file did not become stable within $TimeoutSeconds seconds: $Path"
}

function Get-FreshRunSaves {
    param(
        [Parameter(Mandatory = $true)][string]$SaveDirectory,
        [Parameter(Mandatory = $true)][datetime]$RunStartedUtc
    )

    $cutoff = $RunStartedUtc.AddSeconds(-2)
    $results = @()

    foreach ($file in Get-ChildItem -LiteralPath $SaveDirectory -File -Filter '*.eu4') {
        if ($file.LastWriteTimeUtc -lt $cutoff) {
            continue
        }
        $metadata = Get-Eu4SaveMetadata -Path $file.FullName
        if ($null -ne $metadata) {
            $results += $metadata
        }
    }

    return @($results | Sort-Object SortKey, Name)
}

function Copy-FreshArtifacts {
    param(
        [Parameter(Mandatory = $true)][string]$RunDirectory,
        [Parameter(Mandatory = $true)][string]$SaveDirectory,
        [Parameter(Mandatory = $true)][string]$LogDirectory,
        [Parameter(Mandatory = $true)][datetime]$RunStartedUtc,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$CheckpointSaves,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$ConfigurationFiles
    )

    $saveArchive = Join-Path $RunDirectory 'saves'
    $logArchive = Join-Path $RunDirectory 'logs'
    $configArchive = Join-Path $RunDirectory 'configuration'
    foreach ($directory in @($saveArchive, $logArchive, $configArchive)) {
        if (-not (Test-Path -LiteralPath $directory)) {
            New-Item -ItemType Directory -Path $directory | Out-Null
        }
    }

    $archivedSaves = @()
    foreach ($save in $CheckpointSaves) {
        $destination = Join-Path $saveArchive $save.Name
        Copy-Item -LiteralPath $save.Path -Destination $destination
        $archivedSaves += $destination
    }

    $archivedLogs = @()
    $logCutoff = $RunStartedUtc.AddSeconds(-5)
    foreach ($log in Get-ChildItem -LiteralPath $LogDirectory -File) {
        if ($log.LastWriteTimeUtc -lt $logCutoff) {
            continue
        }
        if ($log.Extension -notin @('.log', '.csv', '.xml')) {
            continue
        }

        $destination = Join-Path $logArchive $log.Name
        Copy-Item -LiteralPath $log.FullName -Destination $destination
        $archivedLogs += $destination
    }

    $archivedConfiguration = @()
    foreach ($configurationFile in $ConfigurationFiles) {
        if (-not (Test-Path -LiteralPath $configurationFile -PathType Leaf)) {
            continue
        }
        $destination = Join-Path $configArchive ([System.IO.Path]::GetFileName($configurationFile))
        Copy-Item -LiteralPath $configurationFile -Destination $destination
        $archivedConfiguration += $destination
    }

    return [pscustomobject]@{
        Saves        = @($archivedSaves)
        Logs         = @($archivedLogs)
        Configuration = @($archivedConfiguration)
    }
}

function New-ObserverCommandBundle {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDirectory,
        [Parameter(Mandatory = $true)][string]$DestinationDirectory,
        [Parameter(Mandatory = $true)][string]$BundlePrefix,
        [switch]$DisableGui
    )

    if (-not (Test-Path -LiteralPath $DestinationDirectory -PathType Container)) {
        throw "Observer command destination does not exist: $DestinationDirectory"
    }

    $sourceFiles = @(Get-ChildItem -LiteralPath $SourceDirectory -File -Filter '*.txt')
    $runtimePaths = @{}
    foreach ($sourceFile in $sourceFiles) {
        $runtimeName = $BundlePrefix + '_' + $sourceFile.Name
        $runtimePath = Join-Path $DestinationDirectory $runtimeName
        if (Test-Path -LiteralPath $runtimePath) {
            throw "Refusing to overwrite observer command file: $runtimePath"
        }
        $runtimePaths[$sourceFile.Name] = $runtimePath
    }

    $encoding = [System.Text.UTF8Encoding]::new($false)
    foreach ($sourceFile in $sourceFiles) {
        $content = Get-Content -LiteralPath $sourceFile.FullName -Raw
        foreach ($referencedFile in $sourceFiles) {
            $sourceReference = 'tests/observer/commands/' + $referencedFile.Name
            $runtimeReference = [System.IO.Path]::GetFileName($runtimePaths[$referencedFile.Name])
            $content = $content.Replace($sourceReference, $runtimeReference)
        }
        if ($DisableGui -and $sourceFile.Name -in @('setup.txt', 'smoke_setup.txt')) {
            $content = [regex]::Replace(
                $content,
                '(?m)^speed 5\s*$',
                'debug_nogui' + [Environment]::NewLine + 'speed 5'
            )
        }
        [System.IO.File]::WriteAllText($runtimePaths[$sourceFile.Name], $content, $encoding)
    }

    return [pscustomobject]@{
        Files = @($runtimePaths.Values | Sort-Object)
    }
}

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$RepoRoot = Get-NormalizedPath -Path $RepoRoot
if ([string]::IsNullOrWhiteSpace($UserDataRoot)) {
    $repoParent = Split-Path -Parent $RepoRoot
    if ((Split-Path -Leaf $repoParent) -eq 'mod') {
        $UserDataRoot = Split-Path -Parent $repoParent
    }
    else {
        $UserDataRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Europa Universalis IV'
    }
}
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $RepoRoot 'diagnostics\observer_runs'
}
$OutputRoot = Assert-OutputRootIsSafe -RepositoryRoot $RepoRoot -CandidateRoot $OutputRoot
$GameExe = Get-NormalizedPath -Path $GameExe
$UserDataRoot = Get-NormalizedPath -Path $UserDataRoot

if ($Seeds.Count -eq 0) {
    throw 'At least one seed is required.'
}
$distinctSeeds = @($Seeds | Sort-Object -Unique)
if ($distinctSeeds.Count -ne $Seeds.Count) {
    throw 'Seeds must be unique within one batch.'
}
if (-not $Smoke -and $Seeds.Count -ne 10) {
    Write-Warning "This invocation contains $($Seeds.Count) seed(s), not the required full batch of 10."
}
if ($Smoke -and $Seeds.Count -ne 1) {
    throw 'Smoke mode accepts exactly one seed.'
}
if ($NoGui -and -not $ForceStopAfterCompletion) {
    throw 'NoGui requires ForceStopAfterCompletion because the game window cannot be closed interactively.'
}

$GameDirectory = Split-Path -Parent $GameExe
$LauncherSettingsPath = Join-Path $GameDirectory 'launcher-settings.json'
$RepoDescriptorPath = Join-Path $RepoRoot 'descriptor.mod'
$DlcLoadPath = Join-Path $UserDataRoot 'dlc_load.json'
$SettingsPath = Join-Path $UserDataRoot 'settings.txt'
$ExternalDescriptorPath = Join-Path $UserDataRoot 'mod\RIP.mod'
$SaveDirectory = Join-Path $UserDataRoot 'save games'
$LogDirectory = Join-Path $UserDataRoot 'logs'
$CommandFileDiskPath = Join-Path $RepoRoot ($CommandFileVirtualPath -replace '/', '\')
$SchemaPath = Join-Path $PSScriptRoot 'run-manifest.schema.json'

$requiredFiles = @(
    $GameExe,
    $LauncherSettingsPath,
    $RepoDescriptorPath,
    $DlcLoadPath,
    $SettingsPath,
    $ExternalDescriptorPath,
    $CommandFileDiskPath,
    $SchemaPath,
    (Join-Path $PSScriptRoot 'commands\checkpoint_1500.txt'),
    (Join-Path $PSScriptRoot 'commands\checkpoint_1550.txt'),
    (Join-Path $PSScriptRoot 'commands\checkpoint_1600.txt'),
    (Join-Path $PSScriptRoot 'commands\checkpoint_1650.txt'),
    (Join-Path $PSScriptRoot 'commands\smoke_setup.txt'),
    (Join-Path $PSScriptRoot 'commands\smoke_checkpoint_1446.txt')
)
foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required file is missing: $requiredFile"
    }
}
foreach ($requiredDirectory in @($SaveDirectory, $LogDirectory)) {
    if (-not (Test-Path -LiteralPath $requiredDirectory -PathType Container)) {
        throw "Required directory is missing: $requiredDirectory"
    }
}

$launcherSettings = Get-Content -LiteralPath $LauncherSettingsPath -Raw | ConvertFrom-Json
$gameVersion = [string]$launcherSettings.rawVersion
$supportedVersion = Get-DescriptorValue -DescriptorPath $RepoDescriptorPath -Key 'supported_version'
if ($gameVersion -ne $supportedVersion) {
    throw "Game/mod version mismatch: game=$gameVersion mod=$supportedVersion"
}

$externalModPath = Get-DescriptorValue -DescriptorPath $ExternalDescriptorPath -Key 'path'
$externalModPath = Get-NormalizedPath -Path ($externalModPath -replace '/', '\')
if (-not $externalModPath.Equals($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RIP.mod points at '$externalModPath', expected '$RepoRoot'."
}

$dlcLoad = Get-Content -LiteralPath $DlcLoadPath -Raw | ConvertFrom-Json
$enabledMods = @($dlcLoad.enabled_mods)
if ($enabledMods.Count -ne 1 -or [string]$enabledMods[0] -ne 'mod/RIP.mod') {
    throw "Expected exactly mod/RIP.mod in dlc_load.json; found: $($enabledMods -join ', ')"
}

$settings = Get-Content -LiteralPath $SettingsPath -Raw
if ($settings -notmatch '(?m)^compress_saves=no\s*$') {
    throw 'Observer completion detection requires compress_saves=no in settings.txt.'
}
if ($settings -notmatch '(?m)^compress_autosave=no\s*$') {
    throw 'Observer checkpoint capture requires compress_autosave=no in settings.txt.'
}
if ($settings -notmatch '(?m)^autosave="YEARLY"\s*$') {
    throw 'Observer checkpoint capture requires autosave="YEARLY" in settings.txt.'
}

$gitState = Get-GitState -RepositoryRoot $RepoRoot
if ($Launch -and $gitState.Dirty -and -not $AllowDirty) {
    throw 'The worktree is dirty. Commit the exact test state or explicitly pass -AllowDirty for a non-release smoke run.'
}

$RuntimeCommandFiles = @()
$RuntimeCommandFilePath = $CommandFileDiskPath
$RuntimeCommandFileArgument = $CommandFileVirtualPath
if ($Launch) {
    $commandBundleName = 'rip_observer_commands_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmssfffZ')
    $commandBundle = New-ObserverCommandBundle `
        -SourceDirectory (Join-Path $PSScriptRoot 'commands') `
        -DestinationDirectory $UserDataRoot `
        -BundlePrefix $commandBundleName `
        -DisableGui:$NoGui
    $RuntimeCommandFiles = @($commandBundle.Files)
    $expectedRuntimeName = $commandBundleName + '_' + [System.IO.Path]::GetFileName($CommandFileDiskPath)
    $RuntimeCommandFilePath = $RuntimeCommandFiles |
        Where-Object { [System.IO.Path]::GetFileName($_) -eq $expectedRuntimeName } |
        Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace([string]$RuntimeCommandFilePath)) {
        throw "Staged setup command was not found: $expectedRuntimeName"
    }
    $RuntimeCommandFileArgument = [System.IO.Path]::GetFileName($RuntimeCommandFilePath)
}

$plannedRuns = @()
for ($index = 0; $index -lt $Seeds.Count; $index++) {
    $seed = $Seeds[$index]
    $quotedUserDataRoot = $UserDataRoot.Replace('"', '\"')
    $arguments = @(
        '-debug_mode',
        '-start_tag=KIE',
        "-seed=$seed",
        "-userdir=`"$quotedUserDataRoot`""
    )
    if ($BootstrapMode -eq 'AutoRun') {
        # EU4 itself prefixes this startup value with `run_commands `.
        $arguments += ("-auto_run=$RuntimeCommandFileArgument")
    }
    $plannedRuns += [pscustomobject]@{
        RunId     = ('run_{0:D2}' -f ($index + 1))
        Seed      = $seed
        Arguments = $arguments
    }
}

$plan = [pscustomobject]@{
    Mode              = $(if ($Launch) { 'launch' } else { 'dry-run' })
    RepositoryRoot    = $RepoRoot
    GitHead           = $gitState.Head
    GitDirty          = $gitState.Dirty
    GameExe           = $GameExe
    GameVersion       = $gameVersion
    EnabledMods       = $enabledMods
    UserDataRoot      = $UserDataRoot
    OutputRoot        = $OutputRoot
    BootstrapMode     = $BootstrapMode
    NoGui              = [bool]$NoGui
    Smoke             = [bool]$Smoke
    TargetYear        = $TargetYear
    ManualConsoleLine = "run_commands `"$RuntimeCommandFileArgument`""
    Runs              = $plannedRuns
}

if (-not $Launch) {
    $plan | ConvertTo-Json -Depth 8
    return
}

if (-not (Test-Path -LiteralPath $OutputRoot)) {
    New-Item -ItemType Directory -Path $OutputRoot | Out-Null
}
$batchPrefix = $(if ($Smoke) { 'smoke' } else { 'observer' })
$batchName = '{0}_{1}' -f $batchPrefix, ([DateTime]::UtcNow.ToString('yyyyMMdd_HHmmssZ'))
$batchDirectory = Join-Path $OutputRoot $batchName
if (Test-Path -LiteralPath $batchDirectory) {
    throw "Refusing to reuse existing batch directory: $batchDirectory"
}
New-Item -ItemType Directory -Path $batchDirectory | Out-Null

$sourceEvidence = New-SourceSnapshot `
    -RepositoryRoot $RepoRoot `
    -SnapshotRoot (Join-Path $batchDirectory 'source_snapshot') `
    -InventoryPath (Join-Path $batchDirectory 'source-inventory.json')

$batchResults = @()
foreach ($plannedRun in $plannedRuns) {
    $preRunFingerprint = Get-InventoryFingerprint -Inventory @(
        Get-SourceInventory -RepositoryRoot $RepoRoot
    )
    if ($preRunFingerprint -ne $sourceEvidence.Fingerprint) {
        throw 'Engine-loaded source changed after the batch snapshot was created.'
    }

    $runDirectory = Join-Path $batchDirectory $plannedRun.RunId
    New-Item -ItemType Directory -Path $runDirectory | Out-Null

    $startedUtc = [DateTime]::UtcNow
    $manifestPath = Join-Path $runDirectory 'manifest.json'
    $manifest = [pscustomobject]@{
        schema_version  = '1.0'
        run_id          = $plannedRun.RunId
        status          = 'running'
        seed            = $plannedRun.Seed
        started_at_utc  = $startedUtc.ToString('o')
        completed_at_utc = $null
        repository      = [pscustomobject]@{
            root         = $RepoRoot
            head         = $gitState.Head
            dirty        = $gitState.Dirty
            status_lines = @($gitState.StatusLines)
            source_snapshot = $sourceEvidence.Root
            source_inventory = $sourceEvidence.Inventory
            source_inventory_sha256 = $sourceEvidence.Fingerprint
            source_file_count = $sourceEvidence.FileCount
        }
        game            = [pscustomobject]@{
            executable        = $GameExe
            version           = $gameVersion
            supported_version = $supportedVersion
            bootstrap_mode    = $BootstrapMode
            no_gui            = [bool]$NoGui
            smoke             = [bool]$Smoke
            command_file      = $RuntimeCommandFileArgument
            arguments         = @($plannedRun.Arguments)
        }
        user_data_root   = $UserDataRoot
        completion       = [pscustomobject]@{
            target_year      = $TargetYear
            detected_save    = $null
            detected_date    = $null
            process_exit_code = $null
            forced_stop      = $false
        }
        artifacts        = [pscustomobject]@{
            saves        = @()
            logs         = @()
            configuration = @()
        }
        errors           = @()
    }
    Write-JsonFile -Path $manifestPath -Value $manifest

    Write-Host "Starting $($plannedRun.RunId), seed $($plannedRun.Seed)."
    $launchParameters = @{
        FilePath         = $GameExe
        WorkingDirectory = $GameDirectory
        ArgumentList     = $plannedRun.Arguments
        PassThru         = $true
    }
    if ($BootstrapMode -eq 'AutoRun') {
        $launchParameters.WindowStyle = 'Hidden'
    }
    $process = Start-Process @launchParameters
    if ($BootstrapMode -eq 'ManualConsole') {
        Write-Host "When the map loads, enter in the EU4 console: run_commands $RuntimeCommandFileArgument"
    }

    $deadlineUtc = $startedUtc.AddMinutes($TimeoutMinutes)
    $endpoint = $null
    $checkpointSaves = @()
    $capturedCheckpointByYear = @{}
    $saveArchive = Join-Path $runDirectory 'saves'
    New-Item -ItemType Directory -Path $saveArchive | Out-Null
    while ([DateTime]::UtcNow -lt $deadlineUtc) {
        $freshSaves = @(Get-FreshRunSaves -SaveDirectory $SaveDirectory -RunStartedUtc $startedUtc)
        foreach ($requiredYear in $RequiredCheckpointYears) {
            if ($capturedCheckpointByYear.ContainsKey($requiredYear)) {
                continue
            }

            $candidate = $freshSaves |
                Where-Object { $_.Year -eq $requiredYear } |
                Sort-Object SortKey, Name |
                Select-Object -Last 1
            if ($null -eq $candidate) {
                continue
            }

            Wait-FileStable -Path $candidate.Path
            $destinationName = 'checkpoint_{0}.eu4' -f $requiredYear
            $destination = Join-Path $saveArchive $destinationName
            Copy-Item -LiteralPath $candidate.Path -Destination $destination
            $captured = Get-Eu4SaveMetadata -Path $destination
            if ($null -eq $captured -or $captured.Year -ne $requiredYear) {
                throw "Archived checkpoint validation failed for year $requiredYear."
            }
            $capturedCheckpointByYear[$requiredYear] = $captured
            Write-Host "Captured checkpoint $requiredYear from $($candidate.Name)."
        }

        $checkpointSaves = @($capturedCheckpointByYear.Values | Sort-Object Year)
        if ($capturedCheckpointByYear.ContainsKey($TargetYear)) {
            $endpoint = $capturedCheckpointByYear[$TargetYear]
        }
        if ($null -ne $endpoint) {
            break
        }

        if ($process.HasExited) {
            break
        }

        Start-Sleep -Seconds $PollSeconds
    }

    if ($null -eq $endpoint) {
        if ($process.HasExited) {
            $manifest.status = 'failed'
            $manifest.errors = @("EU4 exited before the $TargetYear checkpoint was archived.")
        }
        else {
            $manifest.status = 'timed_out'
            $manifest.errors = @("The $TargetYear checkpoint was not archived within $TimeoutMinutes minutes. EU4 was left running.")
        }
    }
    else {
        $manifest.completion.detected_save = $endpoint.Name
        $manifest.completion.detected_date = $endpoint.DateText
        Write-Host "Detected endpoint $($endpoint.Name), date $($endpoint.DateText)."

        $missingCheckpointYears = @(
            $RequiredCheckpointYears | Where-Object {
                $requiredYear = $_
                -not $capturedCheckpointByYear.ContainsKey($requiredYear)
            }
        )

        if (-not $process.HasExited -and $ForceStopAfterCompletion) {
            Start-Sleep -Seconds 3
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit()
            $manifest.completion.forced_stop = $true
        }
        elseif (-not $process.HasExited) {
            Write-Host 'Endpoint is archived. Close EU4 normally to flush logs and continue.'
            $process.WaitForExit()
        }

        if ($missingCheckpointYears.Count -gt 0) {
            $manifest.status = 'failed'
            $manifest.errors = @(
                'Endpoint was reached, but required checkpoint years are missing: ' +
                ($missingCheckpointYears -join ', ')
            )
        }
        else {
            $manifest.status = 'completed'
        }
    }

    $manifest.artifacts.saves = @($checkpointSaves | ForEach-Object { $_.Path })

    if ($process.HasExited) {
        $manifest.completion.process_exit_code = $process.ExitCode
    }

    $configurationFiles = @(
        $DlcLoadPath,
        $SettingsPath,
        $ExternalDescriptorPath,
        $RepoDescriptorPath
    ) + $RuntimeCommandFiles
    $finalArtifacts = Copy-FreshArtifacts `
        -RunDirectory $runDirectory `
        -SaveDirectory $SaveDirectory `
        -LogDirectory $LogDirectory `
        -RunStartedUtc $startedUtc `
        -CheckpointSaves @() `
        -ConfigurationFiles $configurationFiles
    $manifest.artifacts.logs = @($finalArtifacts.Logs)
    $manifest.artifacts.configuration = @($finalArtifacts.Configuration)

    $postRunFingerprint = Get-InventoryFingerprint -Inventory @(
        Get-SourceInventory -RepositoryRoot $RepoRoot
    )
    if ($postRunFingerprint -ne $sourceEvidence.Fingerprint) {
        $manifest.status = 'failed'
        $manifest.errors = @($manifest.errors) + 'Engine-loaded source changed during the run.'
    }

    if ($manifest.status -eq 'completed') {
        $archivedGameLog = $manifest.artifacts.logs |
            Where-Object { [System.IO.Path]::GetFileName($_) -eq 'game.log' } |
            Select-Object -First 1
        if ([string]::IsNullOrWhiteSpace([string]$archivedGameLog)) {
            $manifest.status = 'failed'
            $manifest.errors = @($manifest.errors) + 'Fresh game.log was not archived.'
        }
        else {
            $gameLogText = Get-Content -LiteralPath $archivedGameLog -Raw
            if ($gameLogText -notmatch 'Start-date:\s*1444\.11\.11') {
                $manifest.status = 'failed'
                $manifest.errors = @($manifest.errors) + 'Archived game.log does not prove a 1444.11.11 start.'
            }
        }
    }

    $manifest.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-JsonFile -Path $manifestPath -Value $manifest

    $batchResults += [pscustomobject]@{
        run_id        = $manifest.run_id
        seed          = $manifest.seed
        status        = $manifest.status
        detected_date = $manifest.completion.detected_date
        manifest      = $manifestPath
    }
    Write-JsonFile -Path (Join-Path $batchDirectory 'batch-summary.json') -Value ([pscustomobject]@{
        schema_version = '1.0'
        generated_at_utc = [DateTime]::UtcNow.ToString('o')
        repository_head = $gitState.Head
        source_inventory_sha256 = $sourceEvidence.Fingerprint
        results = @($batchResults)
    })

    if ($manifest.status -ne 'completed') {
        throw "$($plannedRun.RunId) ended with status '$($manifest.status)'; remaining seeds were not started."
    }
}

Write-Host "Observer batch complete. Evidence: $batchDirectory"
