# Server command reference

РЎРїСЂР°РІРѕС‡РЅРёРє РєРѕРјР°РЅРґ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ `t-report` РЅР° Windows-СЃРµСЂРІРµСЂРµ. РћСЃРЅРѕРІРЅРѕР№ РІР°СЂРёР°РЅС‚ Р·Р°РїСѓСЃРєР° вЂ” PowerShell.

Р’ РїСЂРёРјРµСЂР°С… РїР°РїРєР° РїСЂРѕРµРєС‚Р°:

```powershell
D:\t-report
```

Р•СЃР»Рё РїСЂРѕРµРєС‚ Р»РµР¶РёС‚ РІ РґСЂСѓРіРѕР№ РїР°РїРєРµ, Р·Р°РјРµРЅРёС‚Рµ РїСѓС‚СЊ.

## 1. РџРµСЂРµС…РѕРґ РІ РїСЂРѕРµРєС‚

PowerShell:

```powershell
cd D:\t-report
```

CMD:

```cmd
cd /d D:\t-report
```

## 2. РџСЂРѕРІРµСЂРєР° Python

РџСЂРѕРІРµСЂРёС‚СЊ Python Launcher:

```powershell
py --version
```

РџСЂРѕРІРµСЂРёС‚СЊ РѕР±С‹С‡РЅС‹Р№ Python:

```powershell
python --version
```

РџРѕРЅСЏС‚СЊ, РіРґРµ РЅР°С…РѕРґРёС‚СЃСЏ РєРѕРјР°РЅРґР°:

```powershell
Get-Command py
Get-Command python
```

CMD-Р°РЅР°Р»РѕРіРё:

```cmd
where py
where python
```

## 3. РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№

Р§РµСЂРµР· `py`:

```powershell
py -m pip install openpyxl python-docx python-dotenv
```

Р§РµСЂРµР· `python`:

```powershell
python -m pip install openpyxl python-docx python-dotenv
```

РћР±РЅРѕРІРёС‚СЊ `pip`:

```powershell
py -m pip install --upgrade pip
```

РџСЂРѕРІРµСЂРёС‚СЊ СѓСЃС‚Р°РЅРѕРІР»РµРЅРЅС‹Рµ РїР°РєРµС‚С‹:

```powershell
py -m pip list
```

## 4. РќР°СЃС‚СЂРѕР№РєР° `.env`

РћС‚РєСЂС‹С‚СЊ `.env` РІ Р‘Р»РѕРєРЅРѕС‚Рµ:

```powershell
notepad .\.env
```

РџСЂРёРјРµСЂ SMTP-РЅР°СЃС‚СЂРѕРµРє:

```dotenv
T_REPORT_SMTP_HOST=smtp.yandex.ru
T_REPORT_SMTP_PORT=465
T_REPORT_SMTP_USERNAME=sender@yandex.ru
T_REPORT_SMTP_PASSWORD=app_password
T_REPORT_EMAIL_FROM=sender@yandex.ru
T_REPORT_EMAIL_TO=first@example.com,second@example.com;third@example.com
T_REPORT_SMTP_SECURITY=ssl
```

РџРѕР»СѓС‡Р°С‚РµР»РµР№ РјРѕР¶РЅРѕ СЂР°Р·РґРµР»СЏС‚СЊ Р·Р°РїСЏС‚РѕР№, С‚РѕС‡РєРѕР№ СЃ Р·Р°РїСЏС‚РѕР№ РёР»Рё РЅРѕРІРѕР№ СЃС‚СЂРѕРєРѕР№.

## 5. РџСЂРѕРІРµСЂРєР° РёСЃС…РѕРґРЅРѕРіРѕ Excel

РџСЂРѕРІРµСЂРёС‚СЊ, С‡С‚Рѕ С„Р°Р№Р» РµСЃС‚СЊ:

```powershell
Test-Path .\DS.xlsx
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ СЂР°Р·РјРµСЂ Рё РґР°С‚Сѓ РёР·РјРµРЅРµРЅРёСЏ:

```powershell
Get-Item .\DS.xlsx | Select-Object Name,Length,LastWriteTime
```

## 6. Р›РѕРєР°Р»СЊРЅР°СЏ СЃР±РѕСЂРєР° Р±РµР· РѕС‚РїСЂР°РІРєРё

РЎРѕР±СЂР°С‚СЊ email-РїР°РєРµС‚ РІ `output`:

```powershell
py .\report_tool.py --build-email-package --output-dir .\output
```

РўРѕ Р¶Рµ С‡РµСЂРµР· `python`:

```powershell
python .\report_tool.py --build-email-package --output-dir .\output
```

РЎРѕР±СЂР°С‚СЊ РїР°РєРµС‚ РЅР° РєРѕРЅРєСЂРµС‚РЅСѓСЋ РґР°С‚Сѓ:

```powershell
py .\report_tool.py --build-email-package --date 2026-03-30 --output-dir .\output
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ СЃРѕР·РґР°РЅРЅС‹Рµ С„Р°Р№Р»С‹:

```powershell
Get-ChildItem .\output
```

## 7. Preview-СЂРµР¶РёРј

Р’С‹РІРµСЃС‚Рё РѕС‚С‡РµС‚ РІ РєРѕРЅСЃРѕР»СЊ:

```powershell
py .\report_tool.py --preview
```

Preview РЅР° РєРѕРЅРєСЂРµС‚РЅСѓСЋ РґР°С‚Сѓ:

```powershell
py .\report_tool.py --preview --date 2026-03-30
```

РЎРѕС…СЂР°РЅРёС‚СЊ РІС‹РІРѕРґ preview РІ С„Р°Р№Р»:

```powershell
py .\report_tool.py --preview *> .\logs\preview.log
```

## 8. Р СѓС‡РЅР°СЏ РѕС‚РїСЂР°РІРєР° email

РћС‚РїСЂР°РІРёС‚СЊ РЅР° Р°РґСЂРµСЃР° РёР· `.env`:

```powershell
py .\report_tool.py --send --output-dir .\output
```

РћС‚РїСЂР°РІРёС‚СЊ РЅР° РєРѕРЅРєСЂРµС‚РЅСѓСЋ РґР°С‚Сѓ:

```powershell
py .\report_tool.py --send --date 2026-03-30 --output-dir .\output
```

Р’СЂРµРјРµРЅРЅРѕ РїРµСЂРµРѕРїСЂРµРґРµР»РёС‚СЊ РїРѕР»СѓС‡Р°С‚РµР»РµР№ РёР· РєРѕРјР°РЅРґРЅРѕР№ СЃС‚СЂРѕРєРё:

```powershell
py .\report_tool.py --send --email-to "first@example.com,second@example.com" --output-dir .\output
```

Р—Р°РїСѓСЃС‚РёС‚СЊ РѕС‚РїСЂР°РІРєСѓ С‡РµСЂРµР· СЃРµСЂРІРµСЂРЅС‹Р№ wrapper СЃ Р»РѕРіРѕРј:

```powershell
.\scripts\run_weekly_send.ps1
```

Р—Р°РїСѓСЃС‚РёС‚СЊ wrapper С‡РµСЂРµР· `python` РІРјРµСЃС‚Рѕ `py`:

```powershell
.\scripts\run_weekly_send.ps1 -PythonCommand "python"
```

## 9. РџР»Р°РЅРёСЂРѕРІС‰РёРє Windows

РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ РЅР° РєР°Р¶РґС‹Р№ РїРѕРЅРµРґРµР»СЊРЅРёРє РІ 09:00:

```powershell
.\scripts\install_weekly_task.ps1 -RunAt "09:00"
```

РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ РЅР° РґСЂСѓРіРѕРµ РІСЂРµРјСЏ:

```powershell
.\scripts\install_weekly_task.ps1 -RunAt "08:30"
```

РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ СЃ РґСЂСѓРіРёРј РёРјРµРЅРµРј:

```powershell
.\scripts\install_weekly_task.ps1 -TaskName "T-Report Weekly Send Test" -RunAt "09:00"
```

РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ, РµСЃР»Рё РЅР° СЃРµСЂРІРµСЂРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ `python`:

```powershell
.\scripts\install_weekly_task.ps1 -RunAt "09:00" -PythonCommand "python"
```

РџСЂРѕРІРµСЂРёС‚СЊ РЅР°Р»РёС‡РёРµ Р·Р°РґР°С‡Рё:

```powershell
Get-ScheduledTask -TaskName "T-Report Weekly Send"
```

Р—Р°РїСѓСЃС‚РёС‚СЊ Р·Р°РґР°С‡Сѓ РІСЂСѓС‡РЅСѓСЋ:

```powershell
Start-ScheduledTask -TaskName "T-Report Weekly Send"
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ СЃРѕСЃС‚РѕСЏРЅРёРµ Р·Р°РґР°С‡Рё:

```powershell
Get-ScheduledTask -TaskName "T-Report Weekly Send" | Select-Object TaskName,State
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ РїРѕСЃР»РµРґРЅРёР№ СЂРµР·СѓР»СЊС‚Р°С‚ Р·Р°РїСѓСЃРєР°:

```powershell
Get-ScheduledTaskInfo -TaskName "T-Report Weekly Send"
```

РћС‚РєР»СЋС‡РёС‚СЊ Р·Р°РґР°С‡Сѓ:

```powershell
Disable-ScheduledTask -TaskName "T-Report Weekly Send"
```

Р’РєР»СЋС‡РёС‚СЊ Р·Р°РґР°С‡Сѓ:

```powershell
Enable-ScheduledTask -TaskName "T-Report Weekly Send"
```

РЈРґР°Р»РёС‚СЊ Р·Р°РґР°С‡Сѓ:

```powershell
Unregister-ScheduledTask -TaskName "T-Report Weekly Send" -Confirm:$false
```

РћС‚РєСЂС‹С‚СЊ GUI РїР»Р°РЅРёСЂРѕРІС‰РёРєР°:

```powershell
taskschd.msc
```

## 10. Р›РѕРіРё Рё СЂРµР·СѓР»СЊС‚Р°С‚С‹

РЎРѕР·РґР°С‚СЊ РїР°РїРєРё РІСЂСѓС‡РЅСѓСЋ:

```powershell
New-Item -ItemType Directory -Force -Path .\output
New-Item -ItemType Directory -Force -Path .\logs
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ РїРѕСЃР»РµРґРЅРёРµ Р»РѕРіРё:

```powershell
Get-ChildItem .\logs | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

РћС‚РєСЂС‹С‚СЊ РїРѕСЃР»РµРґРЅРёР№ Р»РѕРі:

```powershell
$lastLog = Get-ChildItem .\logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
notepad $lastLog.FullName
```

РџРѕРєР°Р·Р°С‚СЊ РїРѕСЃР»РµРґРЅРёРµ СЃС‚СЂРѕРєРё РїРѕСЃР»РµРґРЅРµРіРѕ Р»РѕРіР°:

```powershell
$lastLog = Get-ChildItem .\logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $lastLog.FullName -Tail 80
```

РћС‡РёСЃС‚РёС‚СЊ СЃС‚Р°СЂС‹Рµ Р»РѕРіРё СЃС‚Р°СЂС€Рµ 30 РґРЅРµР№:

```powershell
Get-ChildItem .\logs\*.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item
```

РџРѕСЃРјРѕС‚СЂРµС‚СЊ РїРѕСЃР»РµРґРЅРёРµ СЃРѕР·РґР°РЅРЅС‹Рµ РѕС‚С‡РµС‚С‹:

```powershell
Get-ChildItem .\output | Sort-Object LastWriteTime -Descending | Select-Object -First 20
```

## 11. Р”РёР°РіРЅРѕСЃС‚РёРєР° SMTP

РџСЂРѕРІРµСЂРёС‚СЊ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ SMTP-С…РѕСЃС‚Р°:

```powershell
Test-NetConnection smtp.yandex.ru -Port 465
```

Р”Р»СЏ STARTTLS-РїРѕСЂС‚Р°:

```powershell
Test-NetConnection smtp.yandex.ru -Port 587
```

РџСЂРѕРІРµСЂРёС‚СЊ С‚РµРєСѓС‰РёРµ SMTP-РїРµСЂРµРјРµРЅРЅС‹Рµ РёР· `.env` РЅСѓР¶РЅРѕ С‡РµСЂРµР· РїСЂРѕСЃРјРѕС‚СЂ С„Р°Р№Р»Р°:

```powershell
notepad .\.env
```

## 12. Р”РёР°РіРЅРѕСЃС‚РёРєР° РѕС€РёР±РѕРє Р·Р°РїСѓСЃРєР°

Р•СЃР»Рё PowerShell Р±Р»РѕРєРёСЂСѓРµС‚ `.ps1`:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Р Р°Р·РѕРІС‹Р№ Р·Р°РїСѓСЃРє Р±РµР· РёР·РјРµРЅРµРЅРёСЏ РїРѕР»РёС‚РёРєРё:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_weekly_send.ps1
```

Р•СЃР»Рё РєРѕРјР°РЅРґР° `py` РЅРµ РЅР°Р№РґРµРЅР°, РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ `python`:

```powershell
python .\report_tool.py --preview
```

Р•СЃР»Рё `python` С‚РѕР¶Рµ РЅРµ РЅР°Р№РґРµРЅ, СѓСЃС‚Р°РЅРѕРІРёС‚СЊ Python Рё РІРєР»СЋС‡РёС‚СЊ РѕРїС†РёСЋ `Add python.exe to PATH`.

Р•СЃР»Рё РЅРµС‚ РїСЂР°РІ РЅР° СЃРѕР·РґР°РЅРёРµ Р·Р°РґР°С‡Рё, РѕС‚РєСЂС‹С‚СЊ PowerShell РѕС‚ РёРјРµРЅРё Р°РґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂР° РёР»Рё СЃРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ С‡РµСЂРµР· РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ, Сѓ РєРѕС‚РѕСЂРѕРіРѕ РµСЃС‚СЊ РїСЂР°РІР°.

## 13. CMD-РІР°СЂРёР°РЅС‚С‹

РџРµСЂРµР№С‚Рё РІ РїСЂРѕРµРєС‚:

```cmd
cd /d D:\t-report
```

Р—Р°РїСѓСЃС‚РёС‚СЊ preview:

```cmd
py report_tool.py --preview
```

РЎРѕР±СЂР°С‚СЊ email-РїР°РєРµС‚:

```cmd
py report_tool.py --build-email-package --output-dir output
```

РћС‚РїСЂР°РІРёС‚СЊ email:

```cmd
py report_tool.py --send --output-dir output
```

Р—Р°РїСѓСЃС‚РёС‚СЊ PowerShell-СЃРєСЂРёРїС‚ РёР· CMD:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_weekly_send.ps1
```

РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ РёР· CMD:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_weekly_task.ps1 -RunAt "09:00"
```

## 14. РџРѕР»РЅС‹Р№ СЃС†РµРЅР°СЂРёР№ РїРµСЂРІРёС‡РЅРѕРіРѕ РґРµРїР»РѕСЏ

```powershell
cd D:\t-report
py --version
py -m pip install openpyxl python-docx python-dotenv
notepad .\.env
Test-Path .\DS.xlsx
py .\report_tool.py --build-email-package --output-dir .\output
py .\report_tool.py --send --output-dir .\output
.\scripts\install_weekly_task.ps1 -RunAt "09:00"
Start-ScheduledTask -TaskName "T-Report Weekly Send"
Get-ScheduledTaskInfo -TaskName "T-Report Weekly Send"
```

## 15. РџРѕР»РЅС‹Р№ СЃС†РµРЅР°СЂРёР№ РµР¶РµРЅРµРґРµР»СЊРЅРѕР№ СЂСѓС‡РЅРѕР№ РїСЂРѕРІРµСЂРєРё

```powershell
cd D:\t-report
Get-Item .\DS.xlsx | Select-Object Name,Length,LastWriteTime
.\scripts\run_weekly_send.ps1
Get-ChildItem .\logs | Sort-Object LastWriteTime -Descending | Select-Object -First 5
Get-ChildItem .\output | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

