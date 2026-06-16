from __future__ import annotations

import base64
import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import time
from urllib import error, parse, request


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_EXPORT_URL_TEMPLATE = "https://www.googleapis.com/drive/v3/files/{spreadsheet_id}/export"
GOOGLE_DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
XLSX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
LogFn = Callable[[str], None]


def noop_log(message: str) -> None:
    return None


class GoogleSheetsSourceError(Exception):
    pass


@dataclass(frozen=True)
class GoogleSheetsConfig:
    spreadsheet_id: str
    credentials_path: Path
    snapshot_dir: Path


def load_google_sheets_config_from_env(base_dir: Path) -> GoogleSheetsConfig | None:
    spreadsheet_id = os.getenv("T_REPORT_GOOGLE_SPREADSHEET_ID", "").strip()
    credentials_path_raw = os.getenv("T_REPORT_GOOGLE_CREDENTIALS_PATH", "").strip()
    snapshot_dir_raw = os.getenv("T_REPORT_GOOGLE_SNAPSHOT_DIR", "").strip()

    if spreadsheet_id == "" and credentials_path_raw == "":
        return None

    if spreadsheet_id == "":
        raise GoogleSheetsSourceError("T_REPORT_GOOGLE_SPREADSHEET_ID is not configured.")

    if credentials_path_raw == "":
        raise GoogleSheetsSourceError("T_REPORT_GOOGLE_CREDENTIALS_PATH is not configured.")

    snapshot_dir = Path(snapshot_dir_raw) if snapshot_dir_raw else base_dir / "input"

    return GoogleSheetsConfig(
        spreadsheet_id=spreadsheet_id,
        credentials_path=Path(credentials_path_raw),
        snapshot_dir=snapshot_dir,
    )


def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class DerReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.index = 0

    def read_byte(self) -> int:
        if self.index >= len(self.data):
            raise GoogleSheetsSourceError("Invalid private_key: unexpected end of DER.")

        value = self.data[self.index]
        self.index += 1
        return value

    def read_length(self) -> int:
        first = self.read_byte()

        if first < 0x80:
            return first

        length_size = first & 0x7F
        if length_size == 0:
            raise GoogleSheetsSourceError("Invalid private_key: indefinite DER length.")

        value = 0
        for _ in range(length_size):
            value = (value << 8) | self.read_byte()

        return value

    def read_tlv(self, expected_tag: int | None = None) -> bytes:
        tag = self.read_byte()

        if expected_tag is not None and tag != expected_tag:
            raise GoogleSheetsSourceError("Invalid private_key: unexpected DER structure.")

        length = self.read_length()
        end_index = self.index + length

        if end_index > len(self.data):
            raise GoogleSheetsSourceError("Invalid private_key: DER length is out of bounds.")

        value = self.data[self.index:end_index]
        self.index = end_index
        return value

    def peek_byte(self) -> int:
        if self.index >= len(self.data):
            raise GoogleSheetsSourceError("Invalid private_key: unexpected end of DER.")

        return self.data[self.index]


def read_der_integer(reader: DerReader) -> int:
    value = reader.read_tlv(0x02)

    if not value:
        raise GoogleSheetsSourceError("Invalid private_key: empty INTEGER value.")

    return int.from_bytes(value, "big", signed=False)


def decode_pem_body(private_key: str) -> bytes:
    lines = [
        line.strip()
        for line in private_key.strip().splitlines()
        if not line.startswith("-----")
    ]

    try:
        return base64.b64decode("".join(lines))
    except Exception as exc:
        raise GoogleSheetsSourceError("Could not read PEM private_key.") from exc


def parse_rsa_private_key(private_key: str) -> tuple[int, int]:
    der = decode_pem_body(private_key)
    top_level = DerReader(DerReader(der).read_tlv(0x30))
    top_level.read_tlv(0x02)

    # Service account keys usually store RSA material as PKCS#8 PrivateKeyInfo:
    # SEQUENCE(version, algorithm, OCTET STRING(RSAPrivateKey)).
    if top_level.peek_byte() == 0x30:
        top_level.read_tlv(0x30)
        rsa_der = top_level.read_tlv(0x04)
        rsa_reader = DerReader(DerReader(rsa_der).read_tlv(0x30))
    else:
        # Fallback for traditional PKCS#1: SEQUENCE(version, n, e, d, ...).
        rsa_reader = DerReader(DerReader(der).read_tlv(0x30))

    rsa_reader.read_tlv(0x02)
    modulus = read_der_integer(rsa_reader)
    read_der_integer(rsa_reader)
    private_exponent = read_der_integer(rsa_reader)

    return modulus, private_exponent


def rsa_sha256_sign(message: bytes, private_key: str) -> bytes:
    modulus, private_exponent = parse_rsa_private_key(private_key)
    key_size_bytes = (modulus.bit_length() + 7) // 8
    digest = hashlib.sha256(message).digest()
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + digest

    padding_size = key_size_bytes - len(digest_info) - 3
    if padding_size < 8:
        raise GoogleSheetsSourceError("Invalid private_key: RSA key is too short.")

    encoded_message = b"\x00\x01" + (b"\xff" * padding_size) + b"\x00" + digest_info
    signature_int = pow(int.from_bytes(encoded_message, "big"), private_exponent, modulus)

    return signature_int.to_bytes(key_size_bytes, "big")


def build_service_account_jwt(credentials: dict[str, object], scope: str) -> str:
    client_email = str(credentials.get("client_email", "")).strip()
    private_key = str(credentials.get("private_key", "")).strip()

    if client_email == "":
        raise GoogleSheetsSourceError("credentials JSON does not contain client_email.")

    if private_key == "":
        raise GoogleSheetsSourceError("credentials JSON does not contain private_key.")

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iss": client_email,
        "scope": scope,
        "aud": GOOGLE_TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }
    signing_input = ".".join(
        [
            base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            base64url_encode(json.dumps(claims, separators=(",", ":")).encode("utf-8")),
        ]
    ).encode("ascii")
    signature = rsa_sha256_sign(signing_input, private_key)

    return f"{signing_input.decode('ascii')}.{base64url_encode(signature)}"


def read_credentials(credentials_path: Path) -> dict[str, object]:
    if not credentials_path.exists():
        raise GoogleSheetsSourceError(f"Google credentials file was not found: {credentials_path}")

    try:
        return json.loads(credentials_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GoogleSheetsSourceError(f"Google credentials file is not valid JSON: {credentials_path}") from exc


def request_access_token(credentials: dict[str, object], log: LogFn = noop_log) -> str:
    log("Google Sheets step: building service account JWT.")
    assertion = build_service_account_jwt(credentials, GOOGLE_DRIVE_READONLY_SCOPE)
    body = parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode("utf-8")
    token_request = request.Request(
        GOOGLE_TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        log("Google Sheets step: requesting access token from Google OAuth.")
        with request.urlopen(token_request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GoogleSheetsSourceError(f"Google did not issue an access token: HTTP {exc.code}. {detail}") from exc
    except error.URLError as exc:
        raise GoogleSheetsSourceError(f"Could not connect to Google OAuth: {exc}") from exc

    access_token = str(payload.get("access_token", "")).strip()
    if access_token == "":
        raise GoogleSheetsSourceError("Google OAuth response did not contain access_token.")

    log("Google Sheets step: access token received.")
    return access_token


def export_google_sheet_to_xlsx(
    spreadsheet_id: str,
    access_token: str,
    output_path: Path,
    log: LogFn = noop_log,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = GOOGLE_DRIVE_EXPORT_URL_TEMPLATE.format(
        spreadsheet_id=parse.quote(spreadsheet_id, safe="")
    )
    url = f"{url}?{parse.urlencode({'mimeType': XLSX_MIME_TYPE})}"
    export_request = request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )

    try:
        log(f"Google Sheets step: exporting spreadsheet to XLSX: {output_path}")
        with request.urlopen(export_request, timeout=120) as response:
            output_path.write_bytes(response.read())
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GoogleSheetsSourceError(f"Google did not export the spreadsheet: HTTP {exc.code}. {detail}") from exc
    except error.URLError as exc:
        raise GoogleSheetsSourceError(f"Could not connect to Google Drive API: {exc}") from exc

    if output_path.stat().st_size == 0:
        raise GoogleSheetsSourceError(f"Google exported an empty file: {output_path}")

    log(f"Google Sheets step: XLSX saved, bytes={output_path.stat().st_size}.")
    return output_path


def clear_google_sheet_snapshots(snapshot_dir: Path, log: LogFn = noop_log) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    deleted_count = 0
    for snapshot_path in snapshot_dir.glob("google_sheet_snapshot_*.xlsx"):
        if snapshot_path.is_file():
            snapshot_path.unlink()
            deleted_count += 1

    log(
        "Google Sheets step: input directory prepared: "
        f"{snapshot_dir}, old snapshot files deleted={deleted_count}."
    )


def download_google_sheet_snapshot(
    config: GoogleSheetsConfig,
    report_date_text: str,
    log: LogFn = noop_log,
) -> Path:
    log(f"Google Sheets step: reading service account JSON: {config.credentials_path}")
    credentials = read_credentials(config.credentials_path)
    access_token = request_access_token(credentials, log=log)
    clear_google_sheet_snapshots(config.snapshot_dir, log=log)
    snapshot_path = config.snapshot_dir / f"google_sheet_snapshot_{report_date_text}.xlsx"

    return export_google_sheet_to_xlsx(config.spreadsheet_id, access_token, snapshot_path, log=log)
