# Compose the missionary book-and-cross art into the existing native policy frame.
# A fixed PNG template retains the gold native frame; its centre is fully
# repainted each run, so the process is deterministic and safe to repeat.
param([switch]$Check)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repoRoot = Split-Path $PSScriptRoot -Parent
$sourcePath = Join-Path $repoRoot 'assets/church_banners/ro_banner_mission_64.png'
$templatePath = Join-Path $repoRoot 'assets/church_banners/ro_policy_frame_template.png'
$outputPng = Join-Path $repoRoot 'diagnostics/church_redesign_20260911/ro_policy_icon.png'
$outputDds = Join-Path $repoRoot 'gfx/interface/rip_ro_mission_policy.dds'
$source = [System.Drawing.Image]::FromFile($sourcePath)
$templateStream = [System.IO.MemoryStream]::new([System.IO.File]::ReadAllBytes($templatePath))
$template = [System.Drawing.Image]::FromStream($templateStream)
$bitmap = [System.Drawing.Bitmap]::new($template)
$template.Dispose(); $templateStream.Dispose()
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$points = [System.Drawing.Point[]]@(
    [System.Drawing.Point]::new(18,9), [System.Drawing.Point]::new(37,9),
    [System.Drawing.Point]::new(46,18), [System.Drawing.Point]::new(46,37),
    [System.Drawing.Point]::new(37,46), [System.Drawing.Point]::new(18,46),
    [System.Drawing.Point]::new(9,37), [System.Drawing.Point]::new(9,18))
$brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255,26,45,49))
foreach ($offset in @(0,56)) {
    $shifted = [System.Drawing.Point[]]@($points | ForEach-Object {
        [System.Drawing.Point]::new($_.X + $offset, $_.Y)
    })
    $graphics.FillPolygon($brush, $shifted)
    $fit = [Math]::Min(34.0/$source.Width,36.0/$source.Height)
    $drawWidth = [int][Math]::Round($source.Width*$fit)
    $drawHeight = [int][Math]::Round($source.Height*$fit)
    $graphics.DrawImage($source, [System.Drawing.Rectangle]::new(
        $offset+[int][Math]::Floor((56-$drawWidth)/2),
        [int][Math]::Floor((56-$drawHeight)/2),$drawWidth,$drawHeight))
}
$graphics.Dispose(); $brush.Dispose(); $source.Dispose()
$stream = [System.IO.MemoryStream]::new()
$writer = [System.IO.BinaryWriter]::new($stream)
$writer.Write([System.Text.Encoding]::ASCII.GetBytes('DDS '))
foreach ($n in @(124,0x100F,56,112,448,0,0)) { $writer.Write([uint32]$n) }
for ($i=0; $i -lt 11; $i++) { $writer.Write([uint32]0) }
foreach ($n in @(32,0x41,0,32,0xFF0000,0xFF00,0xFF,4278190080)) { $writer.Write([uint32]$n) }
foreach ($n in @(0x1000,0,0,0,0)) { $writer.Write([uint32]$n) }
for ($y=0; $y -lt 56; $y++) {
    for ($x=0; $x -lt 112; $x++) {
        $pixel = $bitmap.GetPixel($x,$y)
        $writer.Write([byte]$pixel.B); $writer.Write([byte]$pixel.G)
        $writer.Write([byte]$pixel.R); $writer.Write([byte]$pixel.A)
    }
}
$writer.Flush(); $bytes = $stream.ToArray()
if ($Check) {
    $existing = [System.IO.File]::ReadAllBytes($outputDds)
    $preview = [System.Drawing.Image]::FromFile($outputPng)
    $previewMatch = $preview.Width -eq $bitmap.Width -and $preview.Height -eq $bitmap.Height
    $preview.Dispose()
    if ([Convert]::ToBase64String($existing) -cne [Convert]::ToBase64String($bytes) -or -not $previewMatch) {
        throw 'Missionary Network policy icon is stale.'
    }
} else {
    $bitmap.Save($outputPng,[System.Drawing.Imaging.ImageFormat]::Png)
    [System.IO.File]::WriteAllBytes($outputDds,$bytes)
}
$writer.Dispose(); $stream.Dispose(); $bitmap.Dispose()
Write-Output 'PASS: Missionary Network alert reuses the Mission policy banner in both native frames.'
