from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import Evento

class EventoListView(LoginRequiredMixin, generic.ListView):
    model = Evento
    template_name = 'administracion/evento/evento_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class EventoDetailView(LoginRequiredMixin,generic.DetailView):
    model = Evento
    template_name = 'administracion/evento/evento_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class EventoCreate(LoginRequiredMixin, CreateView):
    model = Evento
    template_name = 'administracion/evento/evento_form.html'
    fields = '__all__'

class EventoUpdate(LoginRequiredMixin, UpdateView):
    model = Evento
    template_name = 'administracion/evento/evento_form.html'
    fields = '__all__'

class EventoDelete(LoginRequiredMixin, DeleteView):
    model = Evento
    template_name = 'administracion/evento/evento_confirm_delete.html'
    success_url = reverse_lazy('eventos')