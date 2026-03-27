from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable

from django.conf import settings
from django.utils import timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

from .models import GoogleSheetsSettings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsConfigError(Exception):
    pass


@dataclass
class GoogleSheetsSyncResult:
    spreadsheet_id: str
    spreadsheet_url: str
    sheet_title: str
    rows_synced: int


DATASET_TITLES = {
    'travelers': 'Viajeros',
    'trips': 'Viajes',
    'bookings': 'Reservas',
    'suppliers': 'Proveedores',
    'expenses': 'Gastos',
    'invoices-issued': 'Facturas emitidas',
    'invoices-received': 'Facturas recibidas',
}


def get_google_sheets_settings() -> GoogleSheetsSettings | None:
    return GoogleSheetsSettings.objects.order_by('id').first()


def _credentials_from_settings(config: GoogleSheetsSettings):
    raw = (config.service_account_json or '').strip()
    if raw:
        try:
            info = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GoogleSheetsConfigError('El JSON de la cuenta de servicio no es válido.') from exc
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    env_path = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', '').strip()
    if env_path:
        return service_account.Credentials.from_service_account_file(env_path, scopes=SCOPES)

    raise GoogleSheetsConfigError('Falta configurar el JSON de la cuenta de servicio de Google Sheets.')


def _build_service(config: GoogleSheetsSettings):
    creds = _credentials_from_settings(config)
    return build('sheets', 'v4', credentials=creds, cache_discovery=False)


def _ensure_spreadsheet(service, config: GoogleSheetsSettings) -> str:
    spreadsheet_id = (config.spreadsheet_id or '').strip()
    if spreadsheet_id:
        service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return spreadsheet_id

    created = service.spreadsheets().create(body={
        'properties': {'title': config.spreadsheet_name or 'GESTOR'},
    }).execute()
    spreadsheet_id = created['spreadsheetId']
    config.spreadsheet_id = spreadsheet_id
    config.last_error = ''
    config.save(update_fields=['spreadsheet_id', 'last_error', 'updated_at'])
    return spreadsheet_id


def _get_sheet_titles(service, spreadsheet_id: str) -> dict[str, int]:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    titles = {}
    for item in meta.get('sheets', []):
        props = item.get('properties', {})
        titles[props.get('title', '')] = props.get('sheetId')
    return titles


def _ensure_sheet(service, spreadsheet_id: str, sheet_title: str):
    titles = _get_sheet_titles(service, spreadsheet_id)
    if sheet_title in titles:
        return
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{'addSheet': {'properties': {'title': sheet_title}}}]},
    ).execute()


def _sheet_title(config: GoogleSheetsSettings, dataset: str) -> str:
    base = DATASET_TITLES.get(dataset, dataset)
    prefix = (config.default_sheet_prefix or 'GESTOR').strip()
    return f'{prefix} · {base}'


def sync_dataset_to_google_sheets(dataset: str, headers: list[str], rows: Iterable[list], *, config: GoogleSheetsSettings | None = None) -> GoogleSheetsSyncResult:
    config = config or get_google_sheets_settings()
    if not config or not config.is_enabled:
        raise GoogleSheetsConfigError('Google Sheets no está activo en la configuración.')

    service = _build_service(config)
    spreadsheet_id = _ensure_spreadsheet(service, config)
    sheet_title = _sheet_title(config, dataset)
    _ensure_sheet(service, spreadsheet_id, sheet_title)

    values = [headers] + [[str(value) if value is not None else '' for value in row] for row in rows]
    range_name = f"'{sheet_title}'!A1"
    service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=sheet_title).execute()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': values},
    ).execute()

    config.last_sync_at = timezone.now()
    config.last_error = ''
    config.save(update_fields=['last_sync_at', 'last_error', 'updated_at'])
    return GoogleSheetsSyncResult(
        spreadsheet_id=spreadsheet_id,
        spreadsheet_url=f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit',
        sheet_title=sheet_title,
        rows_synced=max(len(values) - 1, 0),
    )


def remember_google_sheets_error(exc: Exception, config: GoogleSheetsSettings | None = None):
    config = config or get_google_sheets_settings()
    if not config:
        return
    config.last_error = str(exc)
    config.save(update_fields=['last_error', 'updated_at'])
