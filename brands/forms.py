from django import forms

from apps.configuration.utils import get_currency_choices, get_language_choices

from .models import Brand


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name','legal_name','tax_id','email','phone','website','primary_language','primary_currency','accent_color','is_active']
        labels = {
            'name': 'Nombre comercial', 'legal_name': 'Razón social', 'tax_id': 'CIF / NIF', 'email': 'Email',
            'phone': 'Teléfono', 'website': 'Web', 'primary_language': 'Idioma principal',
            'primary_currency': 'Moneda principal', 'accent_color': 'Color principal', 'is_active': 'Activa',
        }
        widgets = {'accent_color': forms.TextInput(attrs={'type': 'color'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['primary_language'].widget = forms.Select(choices=get_language_choices(['es', 'en']))
        self.fields['primary_currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
