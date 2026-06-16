import os
import unittest
from pathlib import Path
from unittest.mock import patch

from cli_parser import parse_cli
from google_sheets_source import GoogleSheetsConfig, base64url_encode, load_google_sheets_config_from_env
from report_tool import DEFAULT_INPUT_DIR, resolve_excel_path


class GoogleSheetsSourceTests(unittest.TestCase):
    def test_base64url_encode_removes_padding(self) -> None:
        self.assertEqual(base64url_encode(b"test"), "dGVzdA")

    def test_parse_cli_accepts_google_source_arguments(self) -> None:
        command = parse_cli(
            [
                "--preview",
                "--google-spreadsheet-id",
                "sheet-id",
                "--google-credentials-path",
                "credentials.json",
                "--google-snapshot-dir",
                "snapshots",
            ]
        )

        self.assertEqual(command.google_spreadsheet_id_raw, "sheet-id")
        self.assertEqual(command.google_credentials_path_raw, "credentials.json")
        self.assertEqual(command.google_snapshot_dir_raw, "snapshots")

    def test_load_google_sheets_config_from_env_returns_none_when_unconfigured(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(load_google_sheets_config_from_env(Path(".")))

    def test_load_google_sheets_config_from_env_defaults_snapshot_dir_to_input(self) -> None:
        with patch.dict(
            os.environ,
            {
                "T_REPORT_GOOGLE_SPREADSHEET_ID": "sheet-id",
                "T_REPORT_GOOGLE_CREDENTIALS_PATH": "credentials.json",
            },
            clear=True,
        ):
            config = load_google_sheets_config_from_env(Path("project"))

        self.assertIsNotNone(config)
        self.assertEqual(config.snapshot_dir, Path("project") / "input")

    def test_resolve_excel_path_uses_downloaded_google_snapshot(self) -> None:
        command = parse_cli(
            [
                "--preview",
                "--google-spreadsheet-id",
                "sheet-id",
                "--google-credentials-path",
                "credentials.json",
            ]
        )

        with patch(
            "report_tool.download_google_sheet_snapshot",
            return_value=Path("source_snapshots/google_sheet_snapshot_2026-05-25.xlsx"),
        ) as download_mock:
            excel_path = resolve_excel_path(command, "2026-05-25")

        self.assertEqual(excel_path, Path("source_snapshots/google_sheet_snapshot_2026-05-25.xlsx"))
        download_mock.assert_called_once()
        config = download_mock.call_args.args[0]
        self.assertIsInstance(config, GoogleSheetsConfig)
        self.assertEqual(config.spreadsheet_id, "sheet-id")

    def test_resolve_excel_path_defaults_explicit_google_config_to_input(self) -> None:
        command = parse_cli(
            [
                "--preview",
                "--google-spreadsheet-id",
                "sheet-id",
                "--google-credentials-path",
                "credentials.json",
            ]
        )

        with patch(
            "report_tool.download_google_sheet_snapshot",
            return_value=Path("input/google_sheet_snapshot_2026-05-25.xlsx"),
        ) as download_mock:
            resolve_excel_path(command, "2026-05-25")

        config = download_mock.call_args.args[0]
        self.assertEqual(config.snapshot_dir, DEFAULT_INPUT_DIR)

    def test_resolve_excel_path_ignores_snapshot_dir_when_google_source_is_not_configured(self) -> None:
        command = parse_cli(
            [
                "--preview",
                "--google-snapshot-dir",
                "input",
            ]
        )

        excel_path = resolve_excel_path(command, "2026-05-25")

        self.assertEqual(excel_path.name, "DS.xlsx")


if __name__ == "__main__":
    unittest.main()
