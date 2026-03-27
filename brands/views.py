from django.contrib.auth.mixins import LoginRequiredMixin

from apps.core.permissions import ConfigurationManageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import BrandForm
from .models import Brand


class BrandListView(LoginRequiredMixin, ListView):
    model = Brand
    template_name = 'brands/brand_list.html'
    context_object_name = 'brands'


class BrandCreateView(ConfigurationManageMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('brands:list')


class BrandDetailView(LoginRequiredMixin, DetailView):
    model = Brand
    template_name = 'brands/brand_detail.html'
    context_object_name = 'brand'


class BrandUpdateView(ConfigurationManageMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brands/brand_form.html'

    def get_success_url(self):
        return reverse_lazy('brands:detail', kwargs={'pk': self.object.pk})
