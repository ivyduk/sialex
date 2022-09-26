from django.http import HttpResponseRedirect
from django.views import generic
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from administracion.util.filters import PeriodoFilter

from ..models import Periodo, InformacionPreinscripcionFormalizacion
from ..forms import PeriodoForm


class PeriodoListView(LoginRequiredMixin, FilterView):
    model = Periodo
    template_name = 'administracion/periodo/periodo_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'
    filterset_class = PeriodoFilter


class PeriodoDetailView(LoginRequiredMixin,generic.DetailView):
    model = Periodo
    template_name = 'administracion/periodo/periodo_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'


class PeriodoCreate(LoginRequiredMixin, CreateView):
    model = Periodo
    form_class = PeriodoForm
    template_name = 'administracion/periodo/periodo_form.html'
    exclude = ['inicio', 'fin']

    def form_valid(self, form):
        self.object = form.save()
        try:
            mensaje_encontrado = InformacionPreinscripcionFormalizacion.objects.get(periodo=self.object)
        except InformacionPreinscripcionFormalizacion.DoesNotExist:
            mensaje_encontrado = None
        if not mensaje_encontrado:
            mensaje = InformacionPreinscripcionFormalizacion(periodo=self.object)
            mensaje.save()
        return HttpResponseRedirect(self.get_success_url())


class PeriodoUpdate(LoginRequiredMixin, UpdateView):
    model = Periodo
    form_class = PeriodoForm
    template_name = 'administracion/periodo/periodo_form.html'
    exclude = ['inicio', 'fin']


class PeriodoDelete(LoginRequiredMixin, DeleteView):
    model = Periodo
    template_name = 'administracion/periodo/periodo_confirm_delete.html'
    success_url = reverse_lazy('periodos')


def contextualizarPeriodo(request):
    error = False
    periodos = Periodo.objects.filter(activo=True, finalizado=False)
    if request.user.is_authenticated and request.user.groups.filter(
            name__in=['Administrativo', "Funcionario", 'Coordinador', 'Docente']).exists():
        periodos = Periodo.objects.filter(activo=True)
    if 'periodo' in request.POST:
        id = request.POST['periodo']
        if not id:
            error = True
        else:
            periodo = Periodo.objects.get(pk=id)
            request.session["periodo_contextualizado"] = periodo.nombre
            request.session["periodo_contextualizado_id"] = str(periodo.id)
            return render(request, 'administracion/home.html', {'periodo': periodo})
    return render(request, 'cambiocontexto/sf.html', {'error': error, 'periodos': periodos})


def descontextualizarPeriodo(request):
    error = False
    if request.POST:
        del request.session["periodo_contextualizado"]
        del request.session["periodo_contextualizado_id"]
    return render(request, 'administracion/home.html')


def periodoWebservice(request, periodo):
    error = False
    if request.user.is_authenticated:
        from django.core import serializers
        data = get_object_or_404(Periodo, pk=periodo)
        serialized_obj = serializers.serialize('json', [data, ])
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


