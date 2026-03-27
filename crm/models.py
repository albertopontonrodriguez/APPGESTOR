from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.brands.models import Brand
from apps.core.models import TimeStampedModel
from apps.travelers.models import Traveler
from apps.trips.models import Trip


class Lead(TimeStampedModel):
    class Stage(models.TextChoices):
        NEW = 'new', 'Nuevo'
        CONTACTED = 'contacted', 'Contactado'
        PROPOSAL = 'proposal', 'Propuesta enviada'
        NEGOTIATION = 'negotiation', 'Negociación'
        WON = 'won', 'Ganado'
        LOST = 'lost', 'Perdido'
        DORMANT = 'dormant', 'Dormido'

    class Source(models.TextChoices):
        WEB = 'web', 'Web'
        INSTAGRAM = 'instagram', 'Instagram'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        REFERRAL = 'referral', 'Recomendación'
        FAIR = 'fair', 'Feria / evento'
        OTHER = 'other', 'Otro'

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='leads')
    full_name = models.CharField(max_length=160)
    company = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=60, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEB)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='owned_leads',
        null=True,
        blank=True,
    )
    preferred_language = models.CharField(max_length=10, default='es')
    destination_interest = models.CharField(max_length=160, blank=True)
    trip_interest = models.ForeignKey(Trip, on_delete=models.SET_NULL, related_name='interested_leads', null=True, blank=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='EUR')
    next_follow_up = models.DateField(null=True, blank=True)
    converted_traveler = models.ForeignKey(Traveler, on_delete=models.SET_NULL, related_name='source_leads', null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Contacto comercial'
        verbose_name_plural = 'Contactos comerciales'
        ordering = ['stage', 'next_follow_up', 'full_name']

    def __str__(self):
        return self.full_name

    @property
    def is_open(self) -> bool:
        return self.stage not in {self.Stage.WON, self.Stage.LOST, self.Stage.DORMANT}

    @property
    def follow_up_due(self) -> bool:
        return bool(self.next_follow_up and self.is_open and self.next_follow_up <= timezone.localdate())


class LeadActivity(TimeStampedModel):
    class ActivityType(models.TextChoices):
        CALL = 'call', 'Llamada'
        EMAIL = 'email', 'Email'
        MEETING = 'meeting', 'Reunión'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        PROPOSAL = 'proposal', 'Propuesta'
        NOTE = 'note', 'Nota'

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices, default=ActivityType.NOTE)
    activity_at = models.DateTimeField(default=timezone.now)
    summary = models.CharField(max_length=180)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='lead_activities',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Actividad de lead'
        verbose_name_plural = 'Actividades de leads'
        ordering = ['-activity_at', '-created_at']

    def __str__(self):
        return self.summary


class SafeTemplateContext(dict):
    def __missing__(self, key):
        return ''


class EmailTemplate(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='email_templates')
    name = models.CharField(max_length=140)
    language = models.CharField(max_length=10, default='es')
    stage_hint = models.CharField(max_length=20, choices=Lead.Stage.choices, blank=True)
    subject_template = models.CharField(max_length=220)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Plantilla de email'
        verbose_name_plural = 'Plantillas de email'
        ordering = ['brand__name', 'language', 'name']

    def __str__(self):
        return self.name

    @staticmethod
    def build_context(lead: Lead) -> SafeTemplateContext:
        follow_up = lead.next_follow_up.strftime('%d/%m/%Y') if lead.next_follow_up else ''
        return SafeTemplateContext({
            'lead_name': lead.full_name or '',
            'lead_first_name': (lead.full_name.split()[0] if lead.full_name else ''),
            'company': lead.company or '',
            'destination': lead.destination_interest or '',
            'trip_name': lead.trip_interest.name if lead.trip_interest else '',
            'trip_destination': lead.trip_interest.destination if lead.trip_interest else '',
            'brand_name': lead.brand.name if lead.brand_id else '',
            'owner_name': str(lead.owner) if lead.owner_id else '',
            'follow_up_date': follow_up,
            'currency': lead.currency or '',
            'estimated_value': f"{lead.estimated_value:.2f}" if lead.estimated_value is not None else '',
            'email': lead.email or '',
            'phone': lead.phone or '',
        })

    def render_subject(self, lead: Lead) -> str:
        return self.subject_template.format_map(self.build_context(lead))

    def render_body(self, lead: Lead) -> str:
        return self.body_template.format_map(self.build_context(lead))
