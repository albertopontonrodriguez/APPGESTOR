from django.urls import path

from .views import (
    ManagementHomeView,
    NotificationSyncView,
    UserCreateView,
    UserDetailView,
    UserListView,
    UserUpdateView,
    ProfilePasswordChangeView,
)

app_name = 'management_ui'

urlpatterns = [
    path('', ManagementHomeView.as_view(), name='home'),
    path('usuarios/', UserListView.as_view(), name='users_list'),
    path('usuarios/nuevo/', UserCreateView.as_view(), name='users_create'),
    path('usuarios/<int:pk>/', UserDetailView.as_view(), name='users_detail'),
    path('usuarios/<int:pk>/editar/', UserUpdateView.as_view(), name='users_update'),
    path('avisos/sincronizar/', NotificationSyncView.as_view(), name='notifications_sync'),
    path('mi-contrasena/', ProfilePasswordChangeView.as_view(), name='password_change'),
]
