[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$spec = Join-Path $PSScriptRoot "jarvis.spec"

Set-Location $root
& $Python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller is not installed for '$Python'. Install it with: $Python -m pip install pyinstaller"
}

& $Python -m PyInstaller --clean --noconfirm $spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed (exit code $LASTEXITCODE)."
}

$sitePackages = & $Python -c "import sys; print(sys.prefix + r'\Lib\site-packages')"
$internal = Join-Path $root "dist\jarvis\_internal"
Copy-Item (Join-Path $sitePackages "onnxruntime") (Join-Path $internal "onnxruntime") -Recurse -Force
Copy-Item (Join-Path $sitePackages "openwakeword") (Join-Path $internal "openwakeword") -Recurse -Force

Write-Host "Portable bundle: $root\dist\jarvis\jarvis.exe"
