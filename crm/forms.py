from django import forms

from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_currency_choices, get_language_choices, get_status_choices

from .models import EmailTemplate, Lead, LeadActivity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'brand', 'full_name', 'company', 'email', 'phone', 'source', 'stage', 'owner',
            'preferred_language', 'destination_interest', 'trip_interest',
            'estimated_value', 'currency', 'next_follow_up', 'notes'
        ]
        labels = {
            'brand': 'Marca',
            'full_name': 'Nombre completo',
            'company': 'Empresa',
            'email': 'Email',
            'phone': 'Teléfono',
            'source': 'Origen',
            'stage': 'Etapa del embudo',
            'owner': 'Responsable',
            'preferred_language': 'Idioma preferente',
            'destination_interest': 'Destino de interés',
            'trip_interest': 'Viaje de interés',
            'estimated_value': 'Valor estimado',
            'currency': 'Moneda',
            'next_follow_up': 'Próximo seguimiento',
            'notes': 'Notas',
        }
        widgets = {
            'next_follow_up': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_language'].widget = forms.Select(choices=get_language_choices(['es', 'en']))
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
        self.fields['stage'].widget = forms.Select(choices=get_status_choices(StatusCatalog.StatusGroup.LEAD, Lead.Stage.choices))


class LeadActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity_at'].input_formats = ['%Y-%m-%dT%H:%M']

    class Meta:
        model = LeadActivity
        fields = ['activity_type', 'activity_at', 'summary', 'notes']
        labels = {
            'activity_type': 'Tipo de actividad',
            'activity_at': 'Fecha y hora',
            'summary': 'Resumen',
            'notes': 'Detalle',
        }
        widgets = {
            'activity_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['brand', 'name', 'language', 'stage_hint', 'subject_template', 'body_template', 'is_active', 'notes']
        labels = {
            'brand': 'Marca',
            'name': 'Nombre de la plantilla',
            'language': 'Idioma',
            'stage_hint': 'Etapa sugerida',
            'subject_template': 'Asunto',
            'body_template': 'Cuerpo del email',
            'is_active': 'Activa',
            'notes': 'Notas internas',
        }
        widgets = {
            'body_template': forms.Textarea(attrs={'rows': 10}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'subject_template': 'Variables: {lead_name}, {lead_first_name}, {brand_name}, {trip_name}, {destination}, {follow_up_date}.',
            'body_template': 'Puedes usar las mismas variables en el cuerpo del email.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].widget = forms.Select(choices=get_language_choices(['es', 'en']))
