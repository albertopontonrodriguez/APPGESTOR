from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.core.permissions import ConfigurationManageMixin

from .forms import CurrencyForm, GoogleSheetsSettingsForm, LanguageForm, StatusCatalogForm
from .google_sheets import get_google_sheets_settings
from .models import Currency, GoogleSheetsSettings, Language, StatusCatalog


class ConfigurationHomeView(ConfigurationManageMixin, TemplateView):
    template_name = "configuration/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "currencies_count": Currency.objects.count(),
            "languages_count": Language.objects.count(),
            "statuses_count": StatusCatalog.objects.count(),
            "google_sheets_config": get_google_sheets_settings(),
            "status_groups": StatusCatalog.objects.values("status_group").annotate(total=Count("id")).order_by("status_group"),
        })
        return context


class CurrencyListView(ConfigurationManageMixin, ListView):
    model = Currency
    template_name = "configuration/currency_list.html"
    context_object_name = "currencies"


class CurrencyCreateView(ConfigurationManageMixin, CreateView):
    model = Currency
    form_class = CurrencyForm
    template_name = "configuration/currency_form.html"
    success_url = reverse_lazy("configuration:currencies_list")


class CurrencyUpdateView(ConfigurationManageMixin, UpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = "configuration/currency_form.html"
    success_url = reverse_lazy("configuration:currencies_list")


class LanguageListView(ConfigurationManageMixin, ListView):
    model = Language
    template_name = "configuration/language_list.html"
    context_object_name = "languages"


class LanguageCreateView(ConfigurationManageMixin, CreateView):
    model = Language
    form_class = LanguageForm
    template_name = "configuration/language_form.html"
    success_url = reverse_lazy("configuration:languages_list")


class LanguageUpdateView(ConfigurationManageMixin, UpdateView):
    model = Language
    form_class = LanguageForm
    template_name = "configuration/language_form.html"
    success_url = reverse_lazy("configuration:languages_list")


class StatusCatalogListView(ConfigurationManageMixin, ListView):
    model = StatusCatalog
    template_name = "configuration/status_list.html"
    context_object_name = "statuses"

    def get_queryset(self):
        queryset = super().get_queryset()
        status_group = self.request.GET.get("group", "").strip()
        if status_group:
            queryset = queryset.filter(status_group=status_group)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_group"] = self.request.GET.get("group", "").strip()
        context["groups"] = StatusCatalog.StatusGroup.choices
        return context


class StatusCatalogCreateView(ConfigurationManageMixin, CreateView):
    model = StatusCatalog
    form_class = StatusCatalogForm
    template_name = "configuration/status_form.html"
    success_url = reverse_lazy("configuration:statuses_list")


class StatusCatalogUpdateView(ConfigurationManageMixin, UpdateView):
    model = StatusCatalog
    form_class = StatusCatalogForm
    template_name = "configuration/status_form.html"
    success_url = reverse_lazy("configuration:statuses_list")


class GoogleSheetsSettingsView(ConfigurationManageMixin, TemplateView):
    template_name = 'configuration/google_sheets_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_google_sheets_settings() or GoogleSheetsSettings(name='Principal')
        context['form'] = GoogleSheetsSettingsForm(instance=instance)
        context['instance'] = instance if instance.pk else None
        return context

    def post(self, request, *args, **kwargs):
        instance = get_google_sheets_settings()
        form = GoogleSheetsSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de Google Sheets guardada.')
            return redirect('configuration:google_sheets')
        return self.render_to_response({'form': form, 'instance': instance})


class GoogleSheetsResetView(ConfigurationManageMixin, View):
    def post(self, request):
        config = get_google_sheets_settings()
        if config:
            config.spreadsheet_id = ''
            config.last_error = ''
            config.save(update_fields=['spreadsheet_id', 'last_error', 'updated_at'])
            messages.success(request, 'Se ha limpiado la vinculación con la hoja actual. La próxima sincronización creará una nueva o usará la que indiques.')
        return redirect('configuration:google_sheets')
