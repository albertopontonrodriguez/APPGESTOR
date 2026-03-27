from decimal import Decimal
from urllib.parse import quote
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from apps.brands.models import Brand
from apps.core.permissions import OperationsManageMixin
from apps.travelers.models import Traveler

from .forms import EmailTemplateForm, LeadActivityForm, LeadForm
from .models import EmailTemplate, Lead, LeadActivity

User = get_user_model()


class CRMHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        open_leads = Lead.objects.exclude(stage__in=[Lead.Stage.WON, Lead.Stage.LOST, Lead.Stage.DORMANT])
        won_leads = Lead.objects.filter(stage=Lead.Stage.WON)
        pipeline_preview = []
        for code, label in Lead.Stage.choices:
            leads = list(Lead.objects.select_related('brand', 'owner').filter(stage=code).order_by('next_follow_up', 'full_name')[:4])
            pipeline_preview.append({
                'code': code,
                'label': label,
                'leads': leads,
                'total': Lead.objects.filter(stage=code).count(),
            })
        context.update(
            {
                'open_leads_count': open_leads.count(),
                'follow_up_due_count': open_leads.filter(next_follow_up__isnull=False, next_follow_up__lte=timezone.localdate()).count(),
                'won_leads_count': won_leads.count(),
                'pipeline_total': open_leads.aggregate(total=Sum('estimated_value'))['total'] or Decimal('0.00'),
                'urgent_leads': open_leads.filter(Q(next_follow_up__isnull=False)).order_by('next_follow_up', 'stage')[:8],
                'recent_activities': LeadActivity.objects.select_related('lead', 'created_by').order_by('-activity_at')[:10],
                'stage_counts': [
                    {'stage': dict(Lead.Stage.choices).get(row['stage'], row['stage']), 'total': row['total']}
                    for row in Lead.objects.values('stage').annotate(total=Count('id')).order_by('stage')
                ],
                'pipeline_preview': pipeline_preview,
                'email_templates_count': EmailTemplate.objects.filter(is_active=True).count(),
            }
        )
        return context


class CRMPipelineView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/pipeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.request.GET.get('brand', '').strip()
        owner = self.request.GET.get('owner', '').strip()
        source = self.request.GET.get('source', '').strip()
        queryset = Lead.objects.select_related('brand', 'owner', 'trip_interest')
        if brand:
            queryset = queryset.filter(brand_id=brand)
        if owner:
            queryset = queryset.filter(owner_id=owner)
        if source:
            queryset = queryset.filter(source=source)

        columns = []
        for code, label in Lead.Stage.choices:
            stage_qs = queryset.filter(stage=code).order_by('next_follow_up', 'full_name')
            columns.append({
                'code': code,
                'label': label,
                'count': stage_qs.count(),
                'value': stage_qs.aggregate(total=Sum('estimated_value'))['total'] or Decimal('0.00'),
                'leads': list(stage_qs[:25]),
            })

        context.update({
            'columns': columns,
            'brands': Brand.objects.order_by('name'),
            'users': User.objects.filter(is_active=True).order_by('display_name', 'username'),
            'source_choices': Lead.Source.choices,
            'selected_brand': brand,
            'selected_owner': owner,
            'selected_source': source,
            'can_move_leads': self.request.user.is_authenticated and self.request.user.can_manage_operations,
        })
        return context


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'crm/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 30

    def get_queryset(self):
        queryset = Lead.objects.select_related('brand', 'owner', 'trip_interest', 'converted_traveler')
        q = self.request.GET.get('q', '').strip()
        brand = self.request.GET.get('brand', '').strip()
        stage = self.request.GET.get('stage', '').strip()
        source = self.request.GET.get('source', '').strip()
        owner = self.request.GET.get('owner', '').strip()
        follow_up = self.request.GET.get('follow_up', '').strip()
        if q:
            queryset = queryset.filter(Q(full_name__icontains=q) | Q(company__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q) | Q(destination_interest__icontains=q) | Q(trip_interest__name__icontains=q))
        if brand:
            queryset = queryset.filter(brand_id=brand)
        if stage:
            queryset = queryset.filter(stage=stage)
        if source:
            queryset = queryset.filter(source=source)
        if owner:
            queryset = queryset.filter(owner_id=owner)
        if follow_up == 'due':
            queryset = queryset.filter(next_follow_up__isnull=False, next_follow_up__lte=timezone.localdate())
        elif follow_up == 'planned':
            queryset = queryset.filter(next_follow_up__isnull=False)
        return queryset.order_by('stage', 'next_follow_up', 'full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'query': self.request.GET.get('q', '').strip(),
                'selected_brand': self.request.GET.get('brand', '').strip(),
                'selected_stage': self.request.GET.get('stage', '').strip(),
                'selected_source': self.request.GET.get('source', '').strip(),
                'selected_owner': self.request.GET.get('owner', '').strip(),
                'selected_follow_up': self.request.GET.get('follow_up', '').strip(),
                'brands': Brand.objects.order_by('name'),
                'users': User.objects.filter(is_active=True).order_by('display_name', 'username'),
                'stage_choices': Lead.Stage.choices,
                'source_choices': Lead.Source.choices,
            }
        )
        return context


class LeadCreateView(OperationsManageMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'

    def get_success_url(self):
        return reverse_lazy('crm:leads_detail', kwargs={'pk': self.object.pk})


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'crm/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        return Lead.objects.select_related('brand', 'owner', 'trip_interest', 'converted_traveler').prefetch_related('activities', 'tasks', 'calendar_events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template_qs = EmailTemplate.objects.filter(is_active=True).order_by('brand__name', 'language', 'name')
        if self.object.brand_id:
            template_qs = template_qs.filter(brand=self.object.brand)
        context['activity_form'] = LeadActivityForm()
        context['linked_tasks_count'] = self.object.tasks.count()
        context['linked_events_count'] = self.object.calendar_events.count()
        context['email_templates'] = template_qs
        return context


class LeadUpdateView(OperationsManageMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'

    def get_success_url(self):
        return reverse_lazy('crm:leads_detail', kwargs={'pk': self.object.pk})


class LeadActivityCreateView(OperationsManageMixin, CreateView):
    form_class = LeadActivityForm
    template_name = 'crm/activity_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lead = get_object_or_404(Lead, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        activity = form.save(commit=False)
        activity.lead = self.lead
        if self.request.user.is_authenticated:
            activity.created_by = self.request.user
        activity.save()
        return redirect('crm:leads_detail', pk=self.lead.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.lead
        return context


class LeadEmailPreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/lead_email_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = get_object_or_404(Lead.objects.select_related('brand', 'owner', 'trip_interest'), pk=kwargs['pk'])
        templates = EmailTemplate.objects.filter(is_active=True, brand=lead.brand).order_by('language', 'name')
        selected_template = None
        template_id = self.request.GET.get('template', '').strip()
        if template_id:
            selected_template = get_object_or_404(templates, pk=template_id)
        elif templates.exists():
            selected_template = templates.first()

        subject = ''
        body = ''
        mailto_link = ''
        if selected_template:
            subject = selected_template.render_subject(lead)
            body = selected_template.render_body(lead)
            if lead.email:
                mailto_link = f"mailto:{lead.email}?subject={quote(subject)}&body={quote(body)}"

        email_backend_label = 'SMTP real' if settings.EMAIL_BACKEND.endswith('smtp.EmailBackend') else 'Consola / pruebas'

        context.update({
            'lead': lead,
            'email_templates': templates,
            'selected_template': selected_template,
            'rendered_subject': subject,
            'rendered_body': body,
            'mailto_link': mailto_link,
            'email_backend_label': email_backend_label,
            'available_placeholders': [
                'lead_name', 'lead_first_name', 'brand_name', 'trip_name', 'trip_destination',
                'destination', 'owner_name', 'follow_up_date', 'estimated_value', 'currency', 'email', 'phone'
            ],
        })
        return context


class LeadSendEmailView(OperationsManageMixin, View):
    def post(self, request, *args, **kwargs):
        lead = get_object_or_404(Lead.objects.select_related('brand', 'owner', 'trip_interest'), pk=kwargs['pk'])
        template = get_object_or_404(EmailTemplate.objects.filter(is_active=True, brand=lead.brand), pk=request.POST.get('template'))
        if not lead.email:
            messages.error(request, 'Este contacto no tiene email informado.')
            return redirect(f"{reverse_lazy('crm:lead_email_preview', kwargs={'pk': lead.pk})}?template={template.pk}")

        subject = template.render_subject(lead)
        body = template.render_body(lead)
        try:
            sent_count = send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=False,
            )
        except Exception as exc:
            messages.error(request, f'No se pudo enviar el email: {exc}')
            return redirect(f"{reverse_lazy('crm:lead_email_preview', kwargs={'pk': lead.pk})}?template={template.pk}")

        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivity.ActivityType.EMAIL,
            summary=f'Email enviado con plantilla: {template.name}',
            notes=f'Asunto: {subject}',
            created_by=request.user if request.user.is_authenticated else None,
        )
        if sent_count:
            if settings.EMAIL_BACKEND.endswith('smtp.EmailBackend'):
                messages.success(request, f'Email enviado correctamente a {lead.email}.')
            else:
                messages.success(request, 'El email se ha generado con el backend de consola. Revisa la terminal para ver el contenido.')
        else:
            messages.warning(request, 'Django no confirmó ningún envío.')
        return redirect('crm:leads_detail', pk=lead.pk)


class LeadStageMoveView(OperationsManageMixin, View):
    def post(self, request, *args, **kwargs):
        lead = get_object_or_404(Lead, pk=kwargs['pk'])
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            payload = {}
        target_stage = (payload.get('stage') or request.POST.get('stage') or '').strip()
        valid_codes = {code for code, _ in Lead.Stage.choices}
        if target_stage not in valid_codes:
            return JsonResponse({'ok': False, 'error': 'Etapa no válida.'}, status=400)

        previous_stage = lead.stage
        if previous_stage == target_stage:
            return JsonResponse({'ok': True, 'stage': target_stage, 'unchanged': True})

        lead.stage = target_stage
        lead.save(update_fields=['stage', 'updated_at'])
        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivity.ActivityType.NOTE,
            summary=f'Contacto movido de {dict(Lead.Stage.choices).get(previous_stage, previous_stage)} a {dict(Lead.Stage.choices).get(target_stage, target_stage)}',
            notes='Cambio realizado desde el pipeline visual.',
            created_by=request.user if request.user.is_authenticated else None,
        )
        return JsonResponse({'ok': True, 'stage': target_stage, 'label': dict(Lead.Stage.choices).get(target_stage, target_stage)})


class EmailTemplateListView(LoginRequiredMixin, ListView):
    model = EmailTemplate
    template_name = 'crm/email_template_list.html'
    context_object_name = 'templates'
    paginate_by = 30

    def get_queryset(self):
        queryset = EmailTemplate.objects.select_related('brand')
        brand = self.request.GET.get('brand', '').strip()
        language = self.request.GET.get('language', '').strip()
        stage = self.request.GET.get('stage', '').strip()
        active = self.request.GET.get('active', '').strip()
        if brand:
            queryset = queryset.filter(brand_id=brand)
        if language:
            queryset = queryset.filter(language=language)
        if stage:
            queryset = queryset.filter(stage_hint=stage)
        if active == 'yes':
            queryset = queryset.filter(is_active=True)
        elif active == 'no':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('brand__name', 'language', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'brands': Brand.objects.order_by('name'),
            'selected_brand': self.request.GET.get('brand', '').strip(),
            'selected_language': self.request.GET.get('language', '').strip(),
            'selected_stage': self.request.GET.get('stage', '').strip(),
            'selected_active': self.request.GET.get('active', '').strip(),
            'language_choices': [('es', 'Español'), ('en', 'Inglés')],
            'stage_choices': Lead.Stage.choices,
        })
        return context


class EmailTemplateCreateView(OperationsManageMixin, CreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'crm/email_template_form.html'

    def get_success_url(self):
        return reverse_lazy('crm:email_templates_detail', kwargs={'pk': self.object.pk})


class EmailTemplateDetailView(LoginRequiredMixin, DetailView):
    model = EmailTemplate
    template_name = 'crm/email_template_detail.html'
    context_object_name = 'template_obj'


class EmailTemplateUpdateView(OperationsManageMixin, UpdateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'crm/email_template_form.html'

    def get_success_url(self):
        return reverse_lazy('crm:email_templates_detail', kwargs={'pk': self.object.pk})


class LeadConvertView(OperationsManageMixin, View):
    def post(self, request, *args, **kwargs):
        lead = get_object_or_404(Lead, pk=kwargs['pk'])
        if lead.converted_traveler:
            messages.info(request, 'Este contacto ya estaba convertido en viajero.')
            return redirect('crm:leads_detail', pk=lead.pk)

        name_parts = lead.full_name.strip().split()
        first_name = name_parts[0] if name_parts else 'Cliente'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'CRM'
        traveler = Traveler.objects.create(
            brand=lead.brand,
            first_name=first_name,
            last_name=last_name,
            email=lead.email,
            phone=lead.phone,
            preferred_language=lead.preferred_language,
            nationality='',
            notes=f'Creado desde CRM comercial. Fuente: {lead.get_source_display()}.\n\n{lead.notes}'.strip(),
        )
        lead.converted_traveler = traveler
        lead.stage = Lead.Stage.WON
        lead.save(update_fields=['converted_traveler', 'stage', 'updated_at'])
        messages.success(request, 'Contacto convertido en viajero correctamente.')
        return redirect('travelers:detail', pk=traveler.pk)
