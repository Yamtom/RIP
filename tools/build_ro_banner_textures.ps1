# Package generated artwork as native 64px BGRA DDS icons; no repainting.
param([switch]$Check)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repoRoot = Split-Path $PSScriptRoot -Parent
foreach ($key in @('war', 'mercy', 'building', 'mission')) {
    $source = [System.Drawing.Image]::FromFile((Join-Path $repoRoot "assets/church_banners/ro_banner_$key.png"))
    $bitmap = [System.Drawing.Bitmap]::new(64, 64, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.DrawImage($source, [System.Drawing.Rectangle]::new(0, 0, 64, 64))
    $graphics.Dispose()
    $source.Dispose()
    $stream = [System.IO.MemoryStream]::new()
    $writer = [System.IO.BinaryWriter]::new($stream)
    $writer.Write([System.Text.Encoding]::ASCII.GetBytes('DDS '))
    # DDS_HEADER: pitch, dimensions, one surface, uncompressed 32-bit alpha.
    foreach ($n in @(124, 0x100F, 64, 64, 256, 0, 0)) { $writer.Write([uint32]$n) }
    for ($i=0; $i -lt 11; $i++) { $writer.Write([uint32]0) }
    foreach ($n in @(32, 0x41, 0, 32, 0xFF0000, 0xFF00, 0xFF)) { $writer.Write([uint32]$n) }
    $writer.Write([uint32]4278190080)
    foreach ($n in @(0x1000, 0, 0, 0, 0)) { $writer.Write([uint32]$n) }
    for ($y=0; $y -lt 64; $y++) {
        for ($x=0; $x -lt 64; $x++) {
            $pixel = $bitmap.GetPixel($x, $y)
            $writer.Write([byte]$pixel.B); $writer.Write([byte]$pixel.G)
            $writer.Write([byte]$pixel.R); $writer.Write([byte]$pixel.A)
        }
    }
    $writer.Flush()
    $output = Join-Path $repoRoot "gfx/interface/rip_church/ro_banner_$key.dds"
    $bytes = $stream.ToArray()
    if ($Check) {
        if (-not [System.IO.File]::Exists($output) -or
            [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($output)) -cne [Convert]::ToBase64String($bytes)) {
            throw "Stale banner: $key"
        }
    } else {
        [System.IO.File]::WriteAllBytes($output, $bytes)
        $bitmap.Save((Join-Path $repoRoot "assets/church_banners/ro_banner_${key}_64.png"), [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $writer.Dispose(); $stream.Dispose(); $bitmap.Dispose()
}
Write-Output 'PASS: four reproducible 64x64 BGRA banners with alpha.'
