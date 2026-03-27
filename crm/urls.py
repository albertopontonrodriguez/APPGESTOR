from django.urls import path

from .views import (
    CRMHomeView, CRMPipelineView, LeadListView, LeadCreateView, LeadDetailView, LeadUpdateView,
    LeadActivityCreateView, LeadConvertView, LeadEmailPreviewView, LeadSendEmailView, LeadStageMoveView,
    EmailTemplateListView, EmailTemplateCreateView, EmailTemplateDetailView, EmailTemplateUpdateView,
)

app_name = 'crm'

urlpatterns = [
    path('', CRMHomeView.as_view(), name='home'),
    path('pipeline/', CRMPipelineView.as_view(), name='pipeline'),
    path('leads/', LeadListView.as_view(), name='leads_list'),
    path('leads/nuevo/', LeadCreateView.as_view(), name='leads_create'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='leads_detail'),
    path('leads/<int:pk>/editar/', LeadUpdateView.as_view(), name='leads_update'),
    path('leads/<int:pk>/actividad/', LeadActivityCreateView.as_view(), name='activity_create'),
    path('leads/<int:pk>/convertir/', LeadConvertView.as_view(), name='convert'),
    path('leads/<int:pk>/email/', LeadEmailPreviewView.as_view(), name='lead_email_preview'),
    path('leads/<int:pk>/email/enviar/', LeadSendEmailView.as_view(), name='lead_email_send'),
    path('leads/<int:pk>/mover/', LeadStageMoveView.as_view(), name='lead_stage_move'),
    path('plantillas/', EmailTemplateListView.as_view(), name='email_templates_list'),
    path('plantillas/nueva/', EmailTemplateCreateView.as_view(), name='email_templates_create'),
    path('plantillas/<int:pk>/', EmailTemplateDetailView.as_view(), name='email_templates_detail'),
    path('plantillas/<int:pk>/editar/', EmailTemplateUpdateView.as_view(), name='email_templates_update'),
]
