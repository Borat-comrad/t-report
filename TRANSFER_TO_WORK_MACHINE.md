# Transfer to work machine

This package is meant to be copied to the Windows work machine and unpacked as a
project folder, for example:

```powershell
D:\t-report
```

## 1. Unpack

Copy `t-report-transfer-20260616.zip` to the work machine and unpack it so that
`report_tool.py` is in the project root.

## 2. Check secrets and source data

Open `.env` and verify SMTP and Google Sheets values:

```powershell
notepad .\.env
```

Check that `DS.xlsx` exists if the local Excel fallback is needed:

```powershell
Test-Path .\DS.xlsx
```

## 3. Recreate the scheduled task

Run PowerShell from the project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy_windows_scheduled.ps1 -Mode Install -ProjectDir "D:\t-report" -RunAt "09:00" -CleanOutput
```

If the project is in another folder, replace `D:\t-report`.

The script installs required Python packages unless `-SkipDependencyInstall` is
passed, creates or updates the Windows Task Scheduler task named
`T-Report Weekly Send`, and writes logs to `logs`.

## 4. Test once

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy_windows_scheduled.ps1 -Mode Run -ProjectDir "D:\t-report" -CleanOutput
```

Then check the latest log:

```powershell
Get-ChildItem .\logs | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```
