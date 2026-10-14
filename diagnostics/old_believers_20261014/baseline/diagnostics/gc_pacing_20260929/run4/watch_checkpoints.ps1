# Capture five-year engine-save checkpoints from the isolated 50-year run.
$ErrorActionPreference = 'Stop'
$processId = 15396
$targetYear = 1495
$userDir = Join-Path $PSScriptRoot 'userdir'
$savePath = Join-Path $userDir 'save games\autosave.eu4'
$checkpointDir = Join-Path $PSScriptRoot 'checkpoints'
$statusPath = Join-Path $PSScriptRoot 'checkpoint_watch.log'
New-Item -ItemType Directory -Path $checkpointDir -Force | Out-Null
$lastDate = ''

while (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $savePath) {
        try {
            $header = Get-Content -LiteralPath $savePath -TotalCount 2
            $match = [regex]::Match($header[1], '^date=(\d{4})\.(\d{1,2})\.(\d{1,2})$')
            if ($match.Success) {
                $year = [int]$match.Groups[1].Value
                $date = $match.Groups[1].Value + '.' + $match.Groups[2].Value + '.' + $match.Groups[3].Value
                if (($year % 5 -eq 0 -and $year -ge 1450) -or $year -ge $targetYear) {
                    if ($date -ne $lastDate) {
                        $lengthBefore = (Get-Item -LiteralPath $savePath).Length
                        Start-Sleep -Seconds 3
                        $lengthAfter = (Get-Item -LiteralPath $savePath).Length
                        if ($lengthBefore -eq $lengthAfter) {
                            $destination = Join-Path $checkpointDir "checkpoint_$date.eu4"
                            Copy-Item -LiteralPath $savePath -Destination $destination -Force
                            $copiedHeader = Get-Content -LiteralPath $destination -TotalCount 2
                            if ($copiedHeader[1] -ne $header[1]) {
                                throw "Copied checkpoint date mismatch: $destination"
                            }
                            Add-Content -LiteralPath $statusPath -Value "$([DateTime]::Now.ToString('s')) $date $lengthAfter"
                            $lastDate = $date
                            if ($year -ge $targetYear) {
                                break
                            }
                        }
                    }
                }
            }
        }
        catch {
            Add-Content -LiteralPath $statusPath -Value "$([DateTime]::Now.ToString('s')) ERROR $($_.Exception.Message)"
        }
    }
    Start-Sleep -Seconds 30
}
