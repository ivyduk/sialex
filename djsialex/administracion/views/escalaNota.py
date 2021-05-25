from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import EscalaNota

class EscalaNotaListView(LoginRequiredMixin, generic.ListView):
    model = EscalaNota
    template_name = 'administracion/escalaNotas/escalanota_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class EscalaNotaDetailView(LoginRequiredMixin,generic.DetailView):
    model = EscalaNota
    template_name = 'administracion/escalaNotas/escalanota_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class EscalaNotaCreate(LoginRequiredMixin, CreateView):
    model = EscalaNota
    template_name = 'administracion/escalaNotas/escalanota_form.html'
    fields = '__all__'

class EscalaNotaUpdate(LoginRequiredMixin, UpdateView):
    model = EscalaNota
    template_name = 'administracion/escalaNotas/escalanota_form.html'
    fields = '__all__'

class EscalaNotaDelete(LoginRequiredMixin, DeleteView):
    model = EscalaNota
    template_name = 'administracion/escalaNotas/escalanota_confirm_delete.html'
    success_url = reverse_lazy('escala-notas')