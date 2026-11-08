[CmdletBinding()]
param(
    [string]$Executable = "",
    [string]$Arguments = "desktop --require-wakeword",
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$valueName = "Jarvis"

if ($Remove) {
    Remove-ItemProperty -Path $runKey -Name $valueName -ErrorAction SilentlyContinue
    Write-Host "Removed the per-user JARVIS startup entry."
    exit 0
}

if (-not $Executable) {
    $Executable = Join-Path $PSScriptRoot "..\dist\jarvis\jarvis.exe"
}
$Executable = (Resolve-Path $Executable -ErrorAction Stop).Path
$command = ('"{0}" {1}' -f $Executable, $Arguments).Trim()
New-Item -Path $runKey -Force | Out-Null
New-ItemProperty -Path $runKey -Name $valueName -Value $command -PropertyType String -Force | Out-Null
Write-Host "Configured per-user startup: $command"
