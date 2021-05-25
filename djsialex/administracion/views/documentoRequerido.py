from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import DocumentoRequerido

class DocumentoRequeridoListView(LoginRequiredMixin, generic.ListView):
    model = DocumentoRequerido
    template_name = 'administracion/documentoRequerido/documentorequerido_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class DocumentoRequeridoDetailView(LoginRequiredMixin,generic.DetailView):
    model = DocumentoRequerido
    template_name = 'administracion/documentoRequerido/documentorequerido_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class DocumentoRequeridoCreate(LoginRequiredMixin, CreateView):
    model = DocumentoRequerido
    template_name = 'administracion/documentoRequerido/documentorequerido_form.html'
    fields = '__all__'

class DocumentoRequeridoUpdate(LoginRequiredMixin, UpdateView):
    model = DocumentoRequerido
    template_name = 'administracion/documentoRequerido/documentorequerido_form.html'
    fields = '__all__'

class DocumentoRequeridoDelete(LoginRequiredMixin, DeleteView):
    model = DocumentoRequerido
    template_name = 'administracion/documentoRequerido/documentorequerido_confirm_delete.html'
    success_url = reverse_lazy('documentos-requeridos')