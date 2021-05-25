from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from administracion.models import PreinscripcionHorarioCurso, Periodo, OfertaAcademica, ReciboPreinscripcion, \
    DescuentoAplicado, AutorizadoCurso, SaldoAFavor, Beca, Nivel
from administracion.views import horario
from django.db import transaction

from administracion.views.modulesAnulacion import AyudanteAnulacion
from django.contrib import messages

@login_required
def escogerOpcionPreinscripcion(request):

    return render(request, 'administracion/preinscripciones/preinscripcion_opciones.html')

@login_required
def liberarCuposOpcion(request):

    periodo_actual_id = request.session["periodo_contextualizado_id"]
    preinscripciones_vigentes = None

    try:
        periodo_actual = Periodo.objects.get(pk = periodo_actual_id)
    except Periodo.DoesNotExist:
        periodo_actual = None

    ESTADO_PREINSCRITO = 5

    if periodo_actual:
        ofertas_academicas = OfertaAcademica.objects.filter(periodo=periodo_actual)
        niveles_uno = Nivel.objects.filter(orden=1, activo=True)
        preinscripciones_vigentes = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion = ESTADO_PREINSCRITO,
                                                                              horario_cupo__curso__oferta_academica__in=ofertas_academicas,
                                                                              horario_cupo__curso__nivel__in=niveles_uno).all()
        preinscripciones_vigentes = preinscripciones_vigentes.values_list('horario_cupo__curso__nivel__idioma__nombre',
                                                                          'horario_cupo__curso__nivel__nombre',
                                                                          'horario_cupo__curso__nombre',
                                                                          'horario_cupo__horario__nombre').annotate(count=Count('id'))

    return render(request, 'administracion/preinscripciones/preinscripciones_anular.html',
                  {'preinscripciones' : preinscripciones_vigentes, 'periodo': periodo_actual})

def sumarCupo(horario_cupo_dict, horario_cupo, esAutorizado):

    if horario_cupo not in horario_cupo_dict:
        horario_cupo_dict[horario_cupo] = [0,0]
    if esAutorizado:
        horario_cupo_dict[horario_cupo][1] += 1
    else:
        horario_cupo_dict[horario_cupo][0] += 1

@login_required()
def liberarCuposCursoNivel1(request):

    periodo_actual_id = request.session["periodo_contextualizado_id"]
    horario_cupo_dict = {}
    try:
        periodo_actual = Periodo.objects.get(pk=periodo_actual_id)
    except Periodo.DoesNotExist:
        periodo_actual = None

    ESTADO_PREINSCRITO = 5

    if periodo_actual:
        ofertas_academicas = OfertaAcademica.objects.filter(periodo=periodo_actual)
        niveles_uno = Nivel.objects.filter(orden=1, activo=True)
        preinscripciones_vigentes = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion=ESTADO_PREINSCRITO,
                                                                              horario_cupo__curso__oferta_academica__in=ofertas_academicas,
                                                                              horario_cupo__curso__nivel__in=niveles_uno).all()
        for preinscripcion in preinscripciones_vigentes:

            ayudanteAnulacion = AyudanteAnulacion(preinscripcion.persona, periodo_actual, preinscripcion)
            ayudanteAnulacion.anulacionPreinscripcion()
            preinscripcion.estado_preinscripcion = 6  # Cancelado
            preinscripcion.save()

            sumarCupo(horario_cupo_dict, preinscripcion.horario_cupo, ayudanteAnulacion.tieneAutorizacion)

        cupos_regulares_liberados = 0
        cupos_autorizados_liberados = 0

        for horario_cupo in horario_cupo_dict:
            horario_cupo.cupo_disponible += horario_cupo_dict[horario_cupo][0]
            horario_cupo.cupo_disponible_autorizados += horario_cupo_dict[horario_cupo][1]
            horario_cupo.save()
            cupos_regulares_liberados += horario_cupo_dict[horario_cupo][0]
            cupos_autorizados_liberados += horario_cupo_dict[horario_cupo][1]

        messages.add_message(request, messages.SUCCESS,
                             'Se han liberado ' + str(cupos_regulares_liberados) + ' cupos regulares y ' + str(cupos_autorizados_liberados)
                             + ' cupos autorizados en el periodo ' + periodo_actual.nombreAmigable())
    return render(request, 'administracion/preinscripciones/preinscripcion_opciones.html')