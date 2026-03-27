from django.urls import path

from .views import BrandCreateView, BrandDetailView, BrandListView, BrandUpdateView

app_name = 'brands'

urlpatterns = [
    path('', BrandListView.as_view(), name='list'),
    path('nuevo/', BrandCreateView.as_view(), name='create'),
    path('<int:pk>/', BrandDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', BrandUpdateView.as_view(), name='update'),
]
