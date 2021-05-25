from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from administracion.models import Profile, Matricula, PreinscripcionExamen, CalificacionExamen

class BuscarHistoriaAcademicaView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'administracion/historiaAcademica/buscar_historias_academicas.html'

@login_required
def escogerOpcionEstudiante(request):

    return render(request, 'administracion/historiaAcademica/opciones.html')

@login_required
def mostrarHistoriaAcademica(request):

    template_name = 'administracion/historiaAcademica/historia_academica_admin.html'
    context = {}

    if request.method == 'GET':

        query = request.GET.get('q')
        query = query.strip()

        try:
            estudiante = Profile.objects.filter(numero_documento=query).first()
        except Profile.DoesNotExist:
            estudiante = None

        matriculas = Matricula.objects.filter(estudiante=estudiante).all()
        preinscripciones_examen = PreinscripcionExamen.objects.filter(persona=estudiante)
        calificaciones_examen = CalificacionExamen.objects.filter(preinscripcion_examen__in=preinscripciones_examen)
        context = {'matriculas': matriculas, 'calificaciones_examen': calificaciones_examen, 'estudiante': estudiante}

    return render(request, template_name, context)
