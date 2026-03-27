from django.db import models

from apps.core.models import TimeStampedModel


class Brand(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    legal_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    primary_language = models.CharField(max_length=10, default='es')
    primary_currency = models.CharField(max_length=10, default='EUR')
    accent_color = models.CharField(max_length=20, default='#5B7F3A')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
