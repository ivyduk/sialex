from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from ..models import Franja
from ..forms.franjaForms import FranjaCreateForm

class FranjaListView(LoginRequiredMixin,generic.ListView):
    model = Franja
    template_name = 'administracion/franja/franja_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class FranjaDetailView(LoginRequiredMixin,generic.DetailView):
    model = Franja
    template_name = 'administracion/franja/franja_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class FranjaCreate(LoginRequiredMixin, CreateView):
    model = Franja
    template_name = 'administracion/franja/franja_form.html'
    form_class = FranjaCreateForm

    def get(self, request, *args, **kwargs):
        context = {'form': FranjaCreateForm()}
        return render(request, 'administracion/franja/franja_form.html', context)

    def post(self, request, *args, **kwargs):
        form = FranjaCreateForm(request.POST)
        if form.is_valid():
            franja = form.save(commit=False)
            nombre = str(franja.get_dia_display()) + '-' + str(franja.hora_inicio)[0:5] + '-' + str(franja.hora_final)[0:5]
            if Franja.objects.filter(nombre=nombre).exists():
                form.add_error('dia', 'Ya se ha guardado una franja para este día y con estas horas.')
                return render(request, 'administracion/franja/franja_form.html', {'form': form})
            else:
                franja.save()
                messages.success(self.request, 'Franja creada correctamente!')
                return HttpResponseRedirect(reverse_lazy('franja-detail', args=[franja.id]))

class FranjaUpdate(LoginRequiredMixin, UpdateView):
    model = Franja
    template_name = 'administracion/franja/franja_form.html'
    form_class = FranjaCreateForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = FranjaCreateForm(request.POST)
        if form.is_valid():
            nombre = str(form.instance.get_dia_display()) + '-' + str(form.instance.hora_inicio)[0:5] + '-' + str(form.instance.hora_final)[0:5]
            if Franja.objects.filter(nombre=nombre).exists() and self.object.nombre != nombre:
                form.add_error('dia', 'Ya se ha guardado una franja para este día y con estas horas.')
                return render(request, 'administracion/franja/franja_form.html', {'form': form})
            else:
                self.object.hora_inicio = form.cleaned_data['hora_inicio']
                self.object.hora_final = form.cleaned_data['hora_final']
                self.object.dia = form.cleaned_data['dia']
                self.object.save()
                messages.success(self.request, 'Franja actualizada correctamente!')
                return HttpResponseRedirect(reverse_lazy('franja-detail', args=[self.object.id]))

class FranjaDelete(LoginRequiredMixin, DeleteView):
    model = Franja
    template_name = 'administracion/franja/franja_confirm_delete.html'
    success_url = reverse_lazy('franjas')