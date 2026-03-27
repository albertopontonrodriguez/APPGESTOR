from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CEO = 'ceo', 'CEO'
        STAFF = 'staff', 'Equipo'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    display_name = models.CharField(max_length=150, blank=True)


    @property
    def is_admin_or_ceo(self) -> bool:
        return self.role in {self.Role.ADMIN, self.Role.CEO}

    @property
    def can_manage_configuration(self) -> bool:
        return self.is_admin_or_ceo

    @property
    def can_manage_finance(self) -> bool:
        return self.is_admin_or_ceo

    @property
    def can_manage_brands(self) -> bool:
        return self.is_admin_or_ceo

    @property
    def can_manage_operations(self) -> bool:
        return self.role in {self.Role.ADMIN, self.Role.CEO, self.Role.STAFF}

    def __str__(self) -> str:
        return self.display_name or self.get_full_name() or self.username
