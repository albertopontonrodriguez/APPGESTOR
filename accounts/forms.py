from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password

from .models import User


class ManagedUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'display_name',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
        ]
        labels = {
            'username': 'Usuario', 'display_name': 'Nombre visible', 'first_name': 'Nombre',
            'last_name': 'Apellidos', 'email': 'Email', 'role': 'Rol', 'is_active': 'Activo',
        }


class ManagedUserUpdateForm(forms.ModelForm):
    new_password1 = forms.CharField(label='Nueva contraseña', required=False, widget=forms.PasswordInput(render_value=False), help_text='Déjalo vacío para mantener la contraseña actual.')
    new_password2 = forms.CharField(label='Repetir nueva contraseña', required=False, widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = User
        fields = ['username', 'display_name', 'first_name', 'last_name', 'email', 'role', 'is_active']
        labels = {
            'username': 'Usuario', 'display_name': 'Nombre visible', 'first_name': 'Nombre',
            'last_name': 'Apellidos', 'email': 'Email', 'role': 'Rol', 'is_active': 'Activo',
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error('new_password2', 'Las contraseñas no coinciden.')
            if password1:
                validate_password(password1, self.instance)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('new_password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Usuario'}))
    password = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Contraseña actual', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))
    new_password1 = forms.CharField(label='Nueva contraseña', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    new_password2 = forms.CharField(label='Repetir nueva contraseña', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
