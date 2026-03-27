from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class RolePermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = ()
    permission_denied_message = 'No tienes permisos para realizar esta acción.'

    def test_func(self):
        if not self.allowed_roles:
            return True
        user = self.request.user
        return user.is_authenticated and getattr(user, 'role', None) in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect('dashboard')
        return super().handle_no_permission()


class AdminOrCEOMixin(RolePermissionMixin):
    allowed_roles = ('admin', 'ceo')


class OperationsManageMixin(RolePermissionMixin):
    allowed_roles = ('admin', 'ceo', 'staff')


class FinanceManageMixin(RolePermissionMixin):
    allowed_roles = ('admin', 'ceo')


class ConfigurationManageMixin(RolePermissionMixin):
    allowed_roles = ('admin', 'ceo')
