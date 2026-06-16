# Windows test deployment

## Server setup over RDP

1. Copy the project folder to the Windows server.
2. Install Python and dependencies:

```powershell
py -m pip install openpyxl python-docx python-dotenv
```

3. Put the source Excel file at `DS.xlsx` in the project root.
4. Configure `.env` in the project root:

```dotenv
T_REPORT_SMTP_HOST=smtp.yandex.ru
T_REPORT_SMTP_PORT=465
T_REPORT_SMTP_USERNAME=sender@example.com
T_REPORT_SMTP_PASSWORD=app_password
T_REPORT_EMAIL_FROM=sender@example.com
T_REPORT_EMAIL_TO=first@example.com,second@example.com;third@example.com
T_REPORT_SMTP_SECURITY=ssl
```

`T_REPORT_EMAIL_TO` supports recipients separated by comma, semicolon, or new line.

## Google Sheets source

For the Google Sheets contour, the application downloads the spreadsheet as an
`.xlsx` snapshot and then runs the normal report pipeline against that file.

Recommended setup:

1. Create a Google Cloud service account.
2. Enable Google Drive API for the Google Cloud project.
3. Download the service account JSON key to the server.
4. Share the Google spreadsheet with the service account `client_email` from the JSON key.
5. Add these values to `.env`:

```dotenv
T_REPORT_GOOGLE_SPREADSHEET_ID=spreadsheet_id_from_url
T_REPORT_GOOGLE_CREDENTIALS_PATH=C:\secure\t-report-google-service-account.json
T_REPORT_GOOGLE_SNAPSHOT_DIR=C:\t-report\input
```

The spreadsheet must contain sheets named `запросы 2026` and `заказы 2026`.
Downloaded snapshots are refreshed in `T_REPORT_GOOGLE_SNAPSHOT_DIR`. Generated
reports stay in `output` and are not cleaned by the scheduled run.

## Manual smoke test

From the project root:

```powershell
py .\report_tool.py --build-email-package --output-dir .\output
```

To force a local Excel file instead of Google Sheets:

```powershell
py .\report_tool.py --build-email-package --excel-path "C:\path\source.xlsx" --output-dir .\output
```

Then run a real send:

```powershell
py .\report_tool.py --send --output-dir .\output
```

Logs and generated files stay on the server in `output` and `logs`.

## Weekly external trigger

Run PowerShell as the Windows account that should own the task:

```powershell
.\scripts\install_weekly_task.ps1 -RunAt "09:00"
```

This creates a Windows Task Scheduler task named `T-Report Weekly Send`. It starts the send contour every Monday, uses the current date as the report date, writes generated files to `output`, and writes execution logs to `logs`.

For a one-off check of the same contour:

```powershell
.\scripts\run_weekly_send.ps1
```

If the server must run the task while the RDP user is logged off, open Task Scheduler, find `T-Report Weekly Send`, and enable `Run whether user is logged on or not` with the service account credentials.

