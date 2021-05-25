from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import Periodicidad

class PeriodicidadListView(LoginRequiredMixin, generic.ListView):
    model = Periodicidad
    template_name = 'administracion/periodicidad/periodicidad_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class PeriodicidadDetailView(LoginRequiredMixin,generic.DetailView):
    model = Periodicidad
    template_name = 'administracion/periodicidad/periodicidad_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class PeriodicidadCreate(LoginRequiredMixin, CreateView):
    model = Periodicidad
    template_name = 'administracion/periodicidad/periodicidad_form.html'
    fields = '__all__'

class PeriodicidadUpdate(LoginRequiredMixin, UpdateView):
    model = Periodicidad
    template_name = 'administracion/periodicidad/periodicidad_form.html'
    fields = '__all__'

class PeriodicidadDelete(LoginRequiredMixin, DeleteView):
    model = Periodicidad
    template_name = 'administracion/periodicidad/asociar_confirm_delete.html'
    success_url = reverse_lazy('periodicidades')