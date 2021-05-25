from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView, View

from administracion.forms import HorarioAdminForm
from administracion.models import Horario

from django.template import Context, loader

class HorarioListView(LoginRequiredMixin, generic.ListView):
    model = Horario
    template_name = 'administracion/horario/horario_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class HorarioDetailView(LoginRequiredMixin,generic.DetailView):
    model = Horario
    template_name = 'administracion/horario/horario_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class HorarioCreate(LoginRequiredMixin, CreateView):
    #form_class = ContenidoNivelForm
    model = Horario
    template_name = 'administracion/horario/horario_form.html'
    fields = ('franja',)

class HorarioUpdate(LoginRequiredMixin, UpdateView):
    model = Horario
    template_name = 'administracion/horario/horario_form.html'
    fields = '__all__'

class HorarioDelete(LoginRequiredMixin, DeleteView):
    model = Horario
    template_name = 'administracion/horario/horario_confirm_delete.html'
    success_url = reverse_lazy('horario')

@login_required
def horarioCreateForm(request):
    form = HorarioAdminForm
    if request.method == 'POST':
        form = HorarioAdminForm(request.POST)
        horario = form.instance
        if form.is_valid():
            if form.cleaned_data['horario_str']:
                horario = Horario.objects.create(
                    nombre = form.cleaned_data['horario_str'])
                franjas = form.cleaned_data['franjas']
                for franja in franjas:
                    horario.franja.add(franja)
            horario.alias = form.cleaned_data['alias']
            horario.save()
            return render(request, 'administracion/horario/horario_detail.html', {'horario': horario})
        else:
            return render(request, 'administracion/horario/horario_form.html', {'form': form})
    else:
        form = HorarioAdminForm
        return render(request, 'administracion/horario/horario_form.html', {'form': form})

