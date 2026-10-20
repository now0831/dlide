# pptx 슬라이드를 PNG로 내보내고 grid.png(2열) 생성. 사용자가 켜 둔 PowerPoint는 종료하지 않음.
# 사용: powershell -File export_check.ps1 -Pptx <path> -Out <dir>
param([Parameter(Mandatory)][string]$Pptx, [Parameter(Mandatory)][string]$Out)

New-Item -ItemType Directory -Force $Out | Out-Null
Get-ChildItem $Out -Filter "s*.png" -ErrorAction SilentlyContinue | Remove-Item -Force
$full = (Resolve-Path $Pptx).Path
$wasRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$pp = New-Object -ComObject PowerPoint.Application
$p = $pp.Presentations.Open($full, $true, $false, $false)
$i = 1
foreach ($s in $p.Slides) { $s.Export((Join-Path $Out "s$i.png"), "PNG", 1280, 720); $i++ }
$p.Close()
if (-not $wasRunning) { $pp.Quit() }
$count = $i - 1

python -I -c @"
import sys
from PIL import Image
out, n = sys.argv[1], int(sys.argv[2])
ims = [Image.open(f'{out}/s{i}.png').resize((640, 360)) for i in range(1, n + 1)]
g = Image.new('RGB', (1280, 360 * ((n + 1) // 2)), 'white')
for k, im in enumerate(ims): g.paste(im, ((k % 2) * 640, (k // 2) * 360))
g.save(f'{out}/grid.png')
"@ $Out $count
"exported $count slides -> $Out\grid.png"
