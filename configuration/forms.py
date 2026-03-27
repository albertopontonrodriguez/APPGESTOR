from django import forms

from .models import Currency, GoogleSheetsSettings, Language, StatusCatalog


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ["code", "name", "symbol", "is_active", "sort_order"]
        labels = {
            'code': 'Código',
            'name': 'Nombre',
            'symbol': 'Símbolo',
            'is_active': 'Activa',
            'sort_order': 'Orden',
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["code", "name", "is_active", "sort_order"]
        labels = {
            'code': 'Código',
            'name': 'Nombre',
            'is_active': 'Activo',
            'sort_order': 'Orden',
        }


class StatusCatalogForm(forms.ModelForm):
    class Meta:
        model = StatusCatalog
        fields = ["status_group", "code", "label", "is_active", "sort_order"]
        labels = {
            'status_group': 'Grupo',
            'code': 'Código interno',
            'label': 'Etiqueta visible',
            'is_active': 'Activo',
            'sort_order': 'Orden',
        }


class GoogleSheetsSettingsForm(forms.ModelForm):
    class Meta:
        model = GoogleSheetsSettings
        fields = [
            'name', 'is_enabled', 'auto_sync_enabled', 'spreadsheet_name', 'spreadsheet_id',
            'default_sheet_prefix', 'service_account_json',
        ]
        labels = {
            'name': 'Nombre de la conexión',
            'is_enabled': 'Conexión activa',
            'auto_sync_enabled': 'Sincronización automática',
            'spreadsheet_name': 'Nombre de la hoja principal',
            'spreadsheet_id': 'ID de la hoja de Google Sheets',
            'default_sheet_prefix': 'Prefijo para las pestañas',
            'service_account_json': 'JSON de la cuenta de servicio',
        }
        help_texts = {
            'spreadsheet_id': 'Si lo dejas vacío, GESTOR creará una hoja nueva automáticamente la primera vez que sincronices.',
            'service_account_json': 'Pega aquí el JSON completo de la cuenta de servicio de Google con acceso a Google Sheets.',
            'auto_sync_enabled': 'Cuando esté activo, GESTOR actualizará automáticamente las pestañas afectadas al guardar cambios.',
        }
        widgets = {
            'service_account_json': forms.Textarea(attrs={'rows': 12}),
        }
