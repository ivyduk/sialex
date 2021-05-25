from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import ProgramaAcademico

class ProgramaAcademicoListView(LoginRequiredMixin,generic.ListView):
    model = ProgramaAcademico
    template_name = 'administracion/programaAcademico/programaacademico_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class ProgramaAcademicoDetailView(LoginRequiredMixin,generic.DetailView):
    model = ProgramaAcademico
    template_name = 'administracion/programaAcademico/programaacademico_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class ProgramaAcademicoCreate(LoginRequiredMixin, CreateView):
    model = ProgramaAcademico
    template_name = 'administracion/programaAcademico/programaacademico_form.html'
    fields = '__all__'

class ProgramaAcademicoUpdate(LoginRequiredMixin, UpdateView):
    model = ProgramaAcademico
    template_name = 'administracion/programaAcademico/programaacademico_form.html'
    fields = '__all__'

class ProgramaAcademicoDelete(LoginRequiredMixin, DeleteView):
    model = ProgramaAcademico
    template_name = 'administracion/programaAcademico/programaacademico_confirm_delete.html'
    success_url = reverse_lazy('programas')
