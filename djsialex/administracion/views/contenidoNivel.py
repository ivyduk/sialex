from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..forms import ContenidoNivelForm
from ..models import ContenidoNivel

class ContenidoNivelListView(LoginRequiredMixin, generic.ListView):
    model = ContenidoNivel
    template_name = 'administracion/contenidoNivel/contenidonivel_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class ContenidoNivelDetailView(LoginRequiredMixin,generic.DetailView):
    model = ContenidoNivel
    template_name = 'administracion/contenidoNivel/contenidonivel_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class ContenidoCreate(LoginRequiredMixin, CreateView):
    form_class = ContenidoNivelForm
    template_name = 'administracion/contenidoNivel/contenidonivel_form.html'
    #fields = ('alias', 'contenido')

class ContenidoNivelUpdate(LoginRequiredMixin, UpdateView):
    form_class = ContenidoNivelForm
    model = ContenidoNivel
    template_name = 'administracion/contenidoNivel/contenidonivel_form.html'

class ContenidoNivelDelete(LoginRequiredMixin, DeleteView):
    model = ContenidoNivel
    template_name = 'administracion/contenidoNivel/contenidonivel_confirm_delete.html'
    success_url = reverse_lazy('contenido-niveles')