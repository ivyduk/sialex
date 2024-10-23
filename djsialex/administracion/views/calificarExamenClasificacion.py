from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count
from administracion.forms import SeleccionarIdiomaForm
from administracion.models import Docente, Profile, ExamenClasificacion, Periodo, Idioma, PreinscripcionExamen, \
    CalificacionExamen, Nivel, usuarioTieneGrupo
from django.contrib.auth.models import Group
from django.contrib import messages
from django.forms import inlineformset_factory, formset_factory
from datetime import datetime

def isDocente(user):
    persona = Profile.objects.filter(usuario__id=user.id).first()
    return Docente.objects.filter(persona__id=persona.id).exists()



@login_required
def seleccionarIdiomaExamen(request):
    user = request.user
    context_dict = {}

    try:
        periodos = Periodo.objects.filter(
            activo=True,
            finalizado=False,
        )
    except Periodo.DoesNotExist:
        periodos = None

    if request.GET:
        if isDocente(user) or usuarioTieneGrupo(user, "Administrador") or usuarioTieneGrupo(user, 'Coordinador'):
            idioma_id = request.GET['idioma']
            current_idioma = request.GET['idioma']
            try:
                idioma = Idioma.objects.get(pk=idioma_id)
            except Idioma.DoesNotExist:
                idioma = None

            if idioma and periodos:
                personas = Profile.objects.filter(usuario=user)
                docentes = Docente.objects.filter(persona__in=personas)

                # Filtrar idiomas que tienen exámenes clasificatorios en el periodo actual
                idiomas_con_examenes = Idioma.objects.filter(
                    examenclasificacion__periodo__in=periodos
                ).annotate(num_examenes=Count('examenclasificacion')).filter(num_examenes__gt=0).order_by('nombre')

                niveles = Nivel.getNivelesProgramasActivos(idioma_id=idioma_id)

                examenes_clasificacion = ExamenClasificacion.objects.filter(
                periodo__in=periodos, idioma_id=idioma_id, docentes_evaluadores__in=docentes
                ).all().order_by('fecha_hora')

                calificaciones_examen = CalificacionExamen.objects.filter(
                    preinscripcion_examen__examen__in=examenes_clasificacion
                ).all().order_by(
                    'preinscripcion_examen__examen__nombre',
                    'preinscripcion_examen__persona__primer_nombre'
                )

                context_dict = {
                    'idiomas': idiomas_con_examenes,
                    'calificaciones_examen': calificaciones_examen,
                    'current_idioma': current_idioma,
                    'niveles': niveles,
                    'user': user,
                    'idioma_sel': idioma
                }
        else:
            messages.add_message(request, messages.WARNING, 'Usted no se encuentra autorizado para utilizar este servicio')
    else:
        idiomas = Idioma.objects.filter(
            examenclasificacion__periodo__in=periodos
        ).annotate(num_examenes=Count('examenclasificacion')).filter(num_examenes__gt=0).order_by('nombre')

        context_dict = {'idiomas': idiomas, 'user': user}

    return render(request, 'administracion/examenClasificacion/calificar_examen.html', context_dict)






    

@login_required
def calificarExamen(request):

    user = request.user
    if request.method == 'POST':
        evaluador = Docente.objects.filter(persona__usuario=user).first()
        calificacion_id = request.POST['calificacion']
        nivel_id = request.POST['nivel']
        if evaluador:
            try:
                calificacion = CalificacionExamen.objects.get(pk=calificacion_id)
            except CalificacionExamen.DoesNotExist:
                calificacion = None

            try:
                nivel = Nivel.objects.get(pk=nivel_id)
            except Nivel.DoesNotExist:
                nivel = None

            if calificacion:
                calificacion.nivel = nivel
                calificacion.docente_evaluador = evaluador
                calificacion.fecha_hora_calificacion = datetime.now()
                calificacion.save()

    return redirect(request.META['HTTP_REFERER'])
