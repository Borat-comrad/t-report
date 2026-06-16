<#
Usage examples:

Install weekly task with local DS.xlsx:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy_windows_scheduled.ps1 -Mode Install -ProjectDir "C:\t-report" -RunAt "09:00" -CleanOutput

Install weekly task that refreshes DS.xlsx from a network share before sending:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy_windows_scheduled.ps1 -Mode Install -ProjectDir "C:\t-report" -SourceExcel "\\fileserver\reports\DS.xlsx" -RunAt "09:00" -CleanOutput

Run once manually through the same contour:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy_windows_scheduled.ps1 -Mode Run -ProjectDir "C:\t-report" -SourceExcel "\\fileserver\reports\DS.xlsx" -CleanOutput

Note: -CleanOutput is kept for existing scheduled tasks, but now cleans input snapshots only.
#>

param(
    [ValidateSet("Install", "Run")]
    [string]$Mode = "Install",

    [string]$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$TaskName = "T-Report Weekly Send",
    [string]$RunAt = "09:00",
    [string]$DaysOfWeek = "Monday",
    [string]$PythonCommand = "",
    [string]$SourceExcel = "",
    [string]$TargetExcelName = "DS.xlsx",
    [string]$InputDir = "",
    [string]$OutputDir = "",
    [string]$LogDir = "",
    [string]$ReportDate = "",
    [switch]$CleanOutput,
    [switch]$SkipDependencyInstall,
    [switch]$RunNowAfterInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)][string]$Command)

    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Resolve-PythonCommand {
    param([string]$PreferredCommand)

    if ($PreferredCommand.Trim() -ne "") {
        if (-not (Test-CommandAvailable $PreferredCommand) -and -not (Test-Path -LiteralPath $PreferredCommand)) {
            throw "Python command was not found: $PreferredCommand"
        }
        return $PreferredCommand
    }

    if (Test-CommandAvailable "py") {
        return "py"
    }

    if (Test-CommandAvailable "python") {
        return "python"
    }

    throw "Python was not found. Install Python and enable PATH, or pass -PythonCommand."
}

function Assert-PathInsideProject {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ProjectRoot
    )

    $projectFull = (Resolve-FullPath $ProjectRoot).TrimEnd("\")
    $pathFull = (Resolve-FullPath $Path).TrimEnd("\")

    if ($pathFull -ne $projectFull -and -not $pathFull.StartsWith($projectFull + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify a path outside the project directory: $pathFull"
    }
}

function Write-LogLine {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$LogPath = ""
    )

    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Write-Host $line

    if ($LogPath -ne "") {
        Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    }
}

function Initialize-ProjectFolders {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][string]$LogPath
    )

    if (-not (Test-Path -LiteralPath $ProjectRoot)) {
        throw "Project directory was not found: $ProjectRoot"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "report_tool.py"))) {
        throw "report_tool.py was not found in project directory: $ProjectRoot"
    }

    New-Item -ItemType Directory -Force -Path $InputPath | Out-Null
    New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
    New-Item -ItemType Directory -Force -Path $LogPath | Out-Null
}

function Ensure-EnvFile {
    param([Parameter(Mandatory = $true)][string]$ProjectRoot)

    $envPath = Join-Path $ProjectRoot ".env"
    if (Test-Path -LiteralPath $envPath) {
        return
    }

    @(
        "T_REPORT_SMTP_HOST=smtp.yandex.ru",
        "T_REPORT_SMTP_PORT=465",
        "T_REPORT_SMTP_USERNAME=sender@example.com",
        "T_REPORT_SMTP_PASSWORD=app_password",
        "T_REPORT_EMAIL_FROM=sender@example.com",
        "T_REPORT_EMAIL_TO=first@example.com,second@example.com",
        "T_REPORT_SMTP_SECURITY=ssl"
    ) | Set-Content -LiteralPath $envPath -Encoding UTF8

    Write-Warning ".env was created with placeholder values. Fill SMTP settings before real sending."
}

function Install-PythonDependencies {
    param([Parameter(Mandatory = $true)][string]$Python)

    & $Python -m pip install openpyxl python-docx python-dotenv
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed."
    }
}

function Update-ExcelFromSource {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$LogPath
    )

    Write-LogLine "Data source step: removing old Excel: $Target" $LogPath
    Remove-Item -LiteralPath $Target -Force -ErrorAction SilentlyContinue

    if ($Source -match "^(https?|ftp)://") {
        Write-LogLine "Data source step: downloading Excel from URL: $Source" $LogPath
        Invoke-WebRequest -Uri $Source -OutFile $Target
    }
    else {
        Write-LogLine "Data source step: copying Excel from file: $Source" $LogPath
        Copy-Item -LiteralPath $Source -Destination $Target -Force
    }

    if (-not (Test-Path -LiteralPath $Target)) {
        throw "Excel file was not loaded: $Target"
    }

    $excelFile = Get-Item -LiteralPath $Target
    if ($excelFile.Length -le 0) {
        throw "Excel file is empty: $Target"
    }

    Write-LogLine "Data source step: Excel loaded: $($excelFile.FullName), bytes=$($excelFile.Length)" $LogPath
}

function Clear-InputFolder {
    param(
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$LogPath
    )

    Assert-PathInsideProject -Path $InputPath -ProjectRoot $ProjectRoot
    New-Item -ItemType Directory -Force -Path $InputPath | Out-Null

    Write-LogLine "Data source step: cleaning old Google snapshot files from input: $InputPath" $LogPath
    Get-ChildItem -LiteralPath $InputPath -Force -Filter "google_sheet_snapshot_*.xlsx" | Remove-Item -Force
}

function Quote-ForScheduledAction {
    param([Parameter(Mandatory = $true)][string]$Value)

    $doubleQuote = [string][char]34
    $backtick = [string][char]96
    $escaped = $Value.Replace($backtick, $backtick + $backtick)
    $escaped = $escaped.Replace($doubleQuote, $backtick + $doubleQuote)
    return $doubleQuote + $escaped + $doubleQuote
}

function Register-WeeklyTask {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$Task,
        [Parameter(Mandatory = $true)][string]$At,
        [Parameter(Mandatory = $true)][string]$WeekDays
    )

    $actionParts = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", (Quote-ForScheduledAction $ScriptPath),
        "-Mode", "Run",
        "-ProjectDir", (Quote-ForScheduledAction $ProjectRoot),
        "-TaskName", (Quote-ForScheduledAction $Task),
        "-PythonCommand", (Quote-ForScheduledAction $Python),
        "-TargetExcelName", (Quote-ForScheduledAction $TargetExcelName),
        "-InputDir", (Quote-ForScheduledAction $InputPath),
        "-OutputDir", (Quote-ForScheduledAction $OutputPath),
        "-LogDir", (Quote-ForScheduledAction $LogPath)
    )

    if ($SourceExcel.Trim() -ne "") {
        $actionParts += @("-SourceExcel", (Quote-ForScheduledAction $SourceExcel))
    }

    if ($ReportDate.Trim() -ne "") {
        $actionParts += @("-ReportDate", (Quote-ForScheduledAction $ReportDate))
    }

    if ($CleanOutput) {
        $actionParts += "-CleanOutput"
    }

    $actionArgs = $actionParts -join " "
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs -WorkingDirectory $ProjectRoot
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $WeekDays -At $At
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

    Register-ScheduledTask `
        -TaskName $Task `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Refreshes Excel when configured, builds T-Report, and sends the weekly email." `
        -Force | Out-Null

    Write-Host "Scheduled task '$Task' registered for $WeekDays at $At."
}

function Invoke-ReportRun {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string]$InputPath,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][string]$LogRoot,
        [Parameter(Mandatory = $true)][string]$ExcelName,
        [string]$ExcelSource,
        [string]$DateRaw,
        [bool]$ShouldCleanInput
    )

    Initialize-ProjectFolders -ProjectRoot $ProjectRoot -InputPath $InputPath -OutputPath $OutputPath -LogPath $LogRoot

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logPath = Join-Path $LogRoot "deploy-run-$stamp.log"
    New-Item -ItemType File -Force -Path $logPath | Out-Null

    Write-LogLine "Report run started." $logPath
    Write-LogLine "Project: $ProjectRoot" $logPath
    Write-LogLine "Input directory: $InputPath" $logPath
    Write-LogLine "Output directory: $OutputPath" $logPath

    $targetExcel = Join-Path $ProjectRoot $ExcelName
    Assert-PathInsideProject -Path $targetExcel -ProjectRoot $ProjectRoot

    if ($ExcelSource.Trim() -ne "") {
        Update-ExcelFromSource -Source $ExcelSource -Target $targetExcel -LogPath $logPath
    }
    elseif (-not (Test-Path -LiteralPath $targetExcel)) {
        throw "Excel file was not found and -SourceExcel was not provided: $targetExcel"
    }

    if ($ShouldCleanInput) {
        Clear-InputFolder -InputPath $InputPath -ProjectRoot $ProjectRoot -LogPath $logPath
    }

    $reportArgs = @(".\report_tool.py", "--send", "--output-dir", $OutputPath, "--google-snapshot-dir", $InputPath)
    if ($DateRaw.Trim() -ne "") {
        $reportArgs += @("--date", $DateRaw)
    }

    Push-Location $ProjectRoot
    try {
        Write-LogLine "Python: starting report_tool.py." $logPath
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONWARNINGS = "ignore::UserWarning:openpyxl.packaging.relationship"
        & $Python @reportArgs *>&1 | ForEach-Object {
            Write-LogLine "Python: $_" $logPath
        }
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            throw "Report command failed with exit code $exitCode."
        }

        Write-LogLine "Report run finished successfully." $logPath
    }
    finally {
        Pop-Location
    }
}

try {
    $ProjectDir = Resolve-FullPath $ProjectDir

    if ($OutputDir.Trim() -eq "") {
        $OutputDir = Join-Path $ProjectDir "output"
    }
    else {
        $OutputDir = Resolve-FullPath $OutputDir
    }

    if ($InputDir.Trim() -eq "") {
        $InputDir = Join-Path $ProjectDir "input"
    }
    else {
        $InputDir = Resolve-FullPath $InputDir
    }

    if ($LogDir.Trim() -eq "") {
        $LogDir = Join-Path $ProjectDir "logs"
    }
    else {
        $LogDir = Resolve-FullPath $LogDir
    }

    $python = Resolve-PythonCommand $PythonCommand

    if ($Mode -eq "Install") {
        Initialize-ProjectFolders -ProjectRoot $ProjectDir -InputPath $InputDir -OutputPath $OutputDir -LogPath $LogDir
        Ensure-EnvFile -ProjectRoot $ProjectDir

        if (-not $SkipDependencyInstall) {
            Install-PythonDependencies -Python $python
        }

        $scriptPath = Resolve-FullPath $PSCommandPath
        Register-WeeklyTask `
            -ScriptPath $scriptPath `
            -ProjectRoot $ProjectDir `
            -Python $python `
            -InputPath $InputDir `
            -OutputPath $OutputDir `
            -LogPath $LogDir `
            -Task $TaskName `
            -At $RunAt `
            -WeekDays $DaysOfWeek

        if ($RunNowAfterInstall) {
            Start-ScheduledTask -TaskName $TaskName
            Write-Host "Scheduled task '$TaskName' was started."
        }

        Write-Host "Deployment finished."
        Write-Host "Check .env, DS.xlsx, and Task Scheduler before production use."
        exit 0
    }

    Invoke-ReportRun `
        -ProjectRoot $ProjectDir `
        -Python $python `
        -InputPath $InputDir `
        -OutputPath $OutputDir `
        -LogRoot $LogDir `
        -ExcelName $TargetExcelName `
        -ExcelSource $SourceExcel `
        -DateRaw $ReportDate `
        -ShouldCleanInput ([bool]$CleanOutput)

    exit 0
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
