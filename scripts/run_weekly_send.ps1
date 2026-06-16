param(
    [string]$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutputDir = (Join-Path $ProjectDir "output"),
    [string]$LogDir = (Join-Path $ProjectDir "logs"),
    [string]$PythonCommand = "py",
    [string[]]$ExtraArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logPath = Join-Path $LogDir "weekly-send-$stamp.log"
$arguments = @(".\report_tool.py", "--send", "--output-dir", $OutputDir) + $ExtraArgs

Push-Location $ProjectDir
try {
    & $PythonCommand @arguments *>&1 | Tee-Object -FilePath $logPath
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
