from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.http import HttpResponseRedirect
from django_filters.views import FilterView

from administracion.forms.examenClasificacionForms import ExamenClasificacionForm
from administracion.models import ExamenClasificacion, Profile, Periodo, AutorizadoExamen, CalificacionExamen, \
    PreinscripcionExamen, getEstadoPreinscripcion
from datetime import datetime

import json

from administracion.util.filters import ExamenFilter
from administracion.util import CSVWriter
from administracion.views.busqueda_list import BusquedaGenerica


@login_required
def examenClasificacionOpciones(request):
    return render(request, 'administracion/examenClasificacion/examen_clasificacion_opciones.html')


@login_required
def calificacionesExamenClasificacionList(request):

    campos = ['preinscripcion_examen__persona__tipo_documento__nombre',
              'preinscripcion_examen__persona__numero_documento',
              'preinscripcion_examen__examen__periodo__alias',
              'preinscripcion_examen__examen__idioma__alias',
              'preinscripcion_examen__persona__primer_nombre',
              'preinscripcion_examen__persona__segundo_nombre',
              'preinscripcion_examen__persona__primer_apellido',
              'preinscripcion_examen__persona__segundo_apellido',
              'docente_evaluador__persona__primer_nombre',
              'docente_evaluador__persona__primer_apellido',
              'nivel__nombre',
              ]

    busqueda_generica = BusquedaGenerica()

    object_list = CalificacionExamen.objects.filter(preinscripcion_examen__examen__periodo__id=request.session['periodo_contextualizado_id'])
    query_string = request.GET.get('q')

    if query_string:
        consulta = busqueda_generica.get_query(query_string, campos)
        object_list = object_list.filter(consulta).order_by('preinscripcion_examen__examen__idioma__nombre','preinscripcion_examen__persona__numero_documento')

    page = request.GET.get('page')
    paginator = Paginator(object_list, 500)
    try:
        inscritos = paginator.page(page)
    except PageNotAnInteger:
        inscritos = paginator.page(1)
    except EmptyPage:
        inscritos = paginator.page(paginator.num_pages)

    return render(request, 'administracion/examenClasificacion/calificaciones_examen_list.html',
                  {'object_list': inscritos, 'total': len(object_list)})

@login_required
def descargarCalificacionesExamen(request):

    calificaciones = CalificacionExamen.objects.filter(
        preinscripcion_examen__examen__periodo__id=request.session['periodo_contextualizado_id']).order_by('preinscripcion_examen__examen__idioma__nombre','preinscripcion_examen__persona__numero_documento').all()

    data = {}

    for i in range(len(calificaciones)):
        data_calificacion = [calificaciones[i].preinscripcion_examen.persona.tipo_documento.nombre,
                  calificaciones[i].preinscripcion_examen.persona.numero_documento,
                  calificaciones[i].preinscripcion_examen.persona.getNombreCompleto().upper(),
                  calificaciones[i].preinscripcion_examen.examen.periodo.alias,
                  calificaciones[i].preinscripcion_examen.examen.idioma.nombre]
        nivel = 'Sin calificacion'
        docente = ''
        fecha_evaluacion = ''
        if calificaciones[i].nivel:
            nivel = calificaciones[i].nivel.nombre
        if calificaciones[i].docente_evaluador:
            docente = calificaciones[i].docente_evaluador.persona.getNombreCompleto()
        if calificaciones[i].fecha_hora_calificacion:
            fecha_evaluacion = calificaciones[i].fecha_hora_calificacion.strftime("%d/%m/%Y %H:%M")
        data_calificacion.append(nivel)
        data_calificacion.append(calificaciones[i].preinscripcion_examen.examen.nombre),
        data_calificacion.append(calificaciones[i].preinscripcion_examen.examen.fecha_hora.strftime("%d/%m/%Y %H:%M")),
        data_calificacion.append(docente)
        data_calificacion.append(fecha_evaluacion)

        data[i+1] = data_calificacion

    header = ['#','Tipo Documento', 'Documento','Nombre','Periodo','Idioma','Resultado','Examen', 'Fecha examen', 'Docente evaluador', 'Fecha Evaluacion']

    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, 'Calificaciones-Examenes')
    return response

@login_required
def descargarPreinscritosExamen(request, examen):

    try:
        examen_clasficacion = ExamenClasificacion.objects.get(pk=examen)
    except ExamenClasificacion.DoesNotExist:
        examen_clasficacion = None

    if examen_clasficacion:

        preinscripciones = PreinscripcionExamen.objects.filter(examen=examen_clasficacion).order_by('persona__primer_nombre', 'fecha_preinscripcion').all()
        data = {}

        for i in range(len(preinscripciones)):
            data_calificacion = [preinscripciones[i].examen.nombre, preinscripciones[i].examen.idioma.nombre,
                                 preinscripciones[i].examen.periodo.nombreAmigable(), preinscripciones[i].persona.tipo_documento,
                                 preinscripciones[i].persona.numero_documento, preinscripciones[i].persona.getNombreCompleto().upper(),
                                 preinscripciones[i].persona.usuario.email.lower(), getEstadoPreinscripcion(preinscripciones[i].estado_preinscripcion),
                                 preinscripciones[i].fecha_preinscripcion.strftime("%Y/%m/%d  %H:%m"), preinscripciones[i].valor_preinscripcion]
            data[i+1] = data_calificacion

        header = ['#','Examen', 'Idioma', 'Periodo', 'Tipo Documento','Documento','Nombre','Correo','Estado','Fecha preinscripcion', 'Valor preinscripcion',
        ]

        csv_writer = CSVWriter()
        response = csv_writer.download_csv_file(data, header, 'Preinscritos-Examenes')
        return response


class ExamenClasificacionListView(LoginRequiredMixin, FilterView):
    model = ExamenClasificacion
    template_name = 'administracion/examenClasificacion/examenclasificacion_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'
    filterset_class = ExamenFilter

    def get_queryset(self):
        periodo_id = self.request.session["periodo_contextualizado_id"]
        examenes_list = []
        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            periodo = None
        if periodo:
            examenes_list = ExamenClasificacion.objects.filter(periodo=periodo).order_by('periodo')
        return examenes_list


class ExamenClasificacionDetailView(LoginRequiredMixin, generic.DetailView):
    model = ExamenClasificacion
    template_name = 'administracion/examenClasificacion/examenclasificacion_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'


class ExamenClasificacionCreate(LoginRequiredMixin, CreateView):
    form_class = ExamenClasificacionForm
    template_name = 'administracion/examenClasificacion/examenclasificacion_form.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.cupo_disponible = instance.cupo_inicial
        instance.cupo_disponible_autorizado = instance.cupo_autorizado
        instance.save()
        return HttpResponseRedirect(reverse_lazy('examen-clasificacion-detail', args=[instance.id]))


class ExamenClasificacionUpdate(LoginRequiredMixin, UpdateView):
    model = ExamenClasificacion
    form_class = ExamenClasificacionForm
    template_name = 'administracion/examenClasificacion/examenclasificacion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.object

        context['cupos_disponibles'] = instance.cupo_disponible
        context['cupos_autorizados'] = instance.cupo_autorizado
        context['cupos_disponibles_autorizados'] = instance.cupo_disponible_autorizado
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        form.save()
        return HttpResponseRedirect(reverse_lazy('examen-clasificacion-detail', args=[instance.id]))


class ExamenClasificacionDelete(LoginRequiredMixin, DeleteView):
    model = ExamenClasificacion
    template_name = 'administracion/examenClasificacion/examenclasificacion_confirm_delete.html'
    success_url = reverse_lazy('examenes-clasificacion')


def calcularEdad(fechaNacimiento):

    fechaNacimiento = datetime.strptime(str(fechaNacimiento), "%Y-%m-%d")
    now = datetime.now()
    diferencia = now - fechaNacimiento

    return int((diferencia.days + diferencia.seconds/86400.0) / 365.2425)


@login_required
def cargar_examenes_disponibles_admin(request):
    if request.user.is_authenticated:
        periodo = request.session["periodo_contextualizado_id"]
        idioma_id = request.GET.get('idioma')
        if idioma_id:
            try:
                periodo = Periodo.objects.get(pk=periodo)
            except Periodo.DoesNotExist:
                periodo = None

            examenes_por_idioma = ExamenClasificacion.objects.filter(idioma=idioma_id, periodo_id=periodo)

            data = {}
            for i in examenes_por_idioma:
                data[str(i.id)] = i.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})

    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required
def cargar_examenes_disponibles(request):

    if request.user.is_authenticated:
        idioma_id = request.GET.get('idioma')
        if idioma_id:
            try:
                aspirante = Profile.objects.get(pk=request.user.profile.id)
            except Profile.DoesNotExist:
                aspirante = None

            fecha_nacimiento = aspirante.fecha_nacimiento
            edad_aspirante = calcularEdad(fecha_nacimiento)
            examenes_por_idioma = ExamenClasificacion.objects.filter(idioma=idioma_id, edad_minima__lte=edad_aspirante, periodo__activo=True)
            examenes_disponibles = examenes_por_idioma.filter(cupo_disponible__gt=0)
            autorizaciones = AutorizadoExamen.objects.filter(numero_documento=aspirante.numero_documento, estado__in=[1,3], examen__in=examenes_por_idioma).all() #Estado: AUTORIZADO o AUTORIZACION_CANCELADA
            for autorizacion in autorizaciones:

                try:
                    examen = ExamenClasificacion.objects.filter(pk=autorizacion.examen.id, cupo_disponible_autorizado__gt=0)
                except ExamenClasificacion.DoesNotExist:
                    examen = None
                if examen and examen not in examenes_disponibles:
                    examenes_disponibles |= examen
            data = {}
            for i in examenes_disponibles:
                data[str(i.id)] = i.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})

    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def verPreinscritosExamen(request, examen):

    preinscripciones = None

    if request.method == 'GET':

        try:
            examen_clasificacion = ExamenClasificacion.objects.get(pk=examen)
        except ExamenClasificacion.DoesNotExist:
            examen_clasificacion = None


        if examen_clasificacion:

            preinscripciones = PreinscripcionExamen.objects.filter(examen=examen_clasificacion).order_by('persona__primer_nombre', 'fecha_preinscripcion').all()

        return render(request, 'administracion/examenClasificacion/preinscritos_examen.html',
                          {'preinscripciones': preinscripciones, 'examen': examen_clasificacion})

    return render(request, 'administracion/examenClasificacion/preinscritos_examen.html',
                  {'preinscripciones': preinscripciones})


@login_required
def examenFiltros(request):

    if request.method == 'GET':
        form = ExamenClasificacionForm()
    return render(request, 'administracion/inscripcion/examenClasificacion/preinscripcion_examen_filtros.html', {'form': form})


class PreinscritosExamenCalificacionlistView(LoginRequiredMixin, generic.ListView):
    model = PreinscripcionExamen
    template_name = 'administracion/inscripcion/examenClasificacion/preinscripcion_examen_listado.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'
    examen_calificacion = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen = self.request.GET.get('examen')
        context['examen'] = ExamenClasificacion.objects.get(pk=examen)
        return context

    def get_queryset(self):
        examen = self.request.GET.get('examen')

        try:
            examen_clasificacion = ExamenClasificacion.objects.get(pk=examen)
        except ExamenClasificacion.DoesNotExist:
            examen_clasificacion = None

        if examen_clasificacion:
            preinscripciones = PreinscripcionExamen.objects.filter(examen=examen_clasificacion).order_by('persona__primer_nombre', 'fecha_preinscripcion').all()
        return list(preinscripciones)