from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import Idioma

class IdiomaListView(LoginRequiredMixin,generic.ListView):
    model = Idioma
    template_name = 'administracion/idioma/idioma_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class IdiomaDetailView(LoginRequiredMixin,generic.DetailView):
    model = Idioma
    template_name = 'administracion/idioma/idioma_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class IdiomaCreate(LoginRequiredMixin, CreateView):
    model = Idioma
    template_name = 'administracion/idioma/idioma_form.html'
    fields = '__all__'

class IdiomaUpdate(LoginRequiredMixin, UpdateView):
    model = Idioma
    template_name = 'administracion/idioma/idioma_form.html'
    fields = '__all__'

class IdiomaDelete(LoginRequiredMixin, DeleteView):
    model = Idioma
    template_name = 'administracion/idioma/idioma_confirm_delete.html'

    success_url = reverse_lazy('idiomas')