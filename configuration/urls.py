from django.urls import path

from .views import (
    ConfigurationHomeView,
    CurrencyCreateView,
    CurrencyListView,
    CurrencyUpdateView,
    GoogleSheetsResetView,
    GoogleSheetsSettingsView,
    LanguageCreateView,
    LanguageListView,
    LanguageUpdateView,
    StatusCatalogCreateView,
    StatusCatalogListView,
    StatusCatalogUpdateView,
)

app_name = "configuration"

urlpatterns = [
    path("", ConfigurationHomeView.as_view(), name="home"),
    path("monedas/", CurrencyListView.as_view(), name="currencies_list"),
    path("monedas/nueva/", CurrencyCreateView.as_view(), name="currencies_create"),
    path("monedas/<int:pk>/editar/", CurrencyUpdateView.as_view(), name="currencies_update"),
    path("idiomas/", LanguageListView.as_view(), name="languages_list"),
    path("idiomas/nuevo/", LanguageCreateView.as_view(), name="languages_create"),
    path("idiomas/<int:pk>/editar/", LanguageUpdateView.as_view(), name="languages_update"),
    path("estados/", StatusCatalogListView.as_view(), name="statuses_list"),
    path("estados/nuevo/", StatusCatalogCreateView.as_view(), name="statuses_create"),
    path("estados/<int:pk>/editar/", StatusCatalogUpdateView.as_view(), name="statuses_update"),
    path('google-sheets/', GoogleSheetsSettingsView.as_view(), name='google_sheets'),
    path('google-sheets/reset/', GoogleSheetsResetView.as_view(), name='google_sheets_reset'),
]
