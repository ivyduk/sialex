from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from administracion.models import Profile, Matricula, Periodo, Curso, Calificacion, TipoDocente, DocentesGrupoAcademico, \
    Observacion, FallaAsistencia, CalificacionExamen, PreinscripcionExamen

from ..report import funcion


@login_required
def misCursosList(request):

    template_name = 'administracion/historiaAcademica/mis_cursos.html'
    context = {}
    estudiante = Profile.objects.get(usuario=request.user)

    if request.method == 'GET' and estudiante:
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado_matricula__in=[7, 9]  # 7 En curso 9 Aprobado - Pendiente en formalizacion
        )
        context = {'matriculas': matriculas}

    return render(request, template_name, context)


@login_required
def miHistoriaAcademica(request):

    template_name = 'administracion/historiaAcademica/mi_historia_academica.html'
    context = {}
    estudiante = Profile.objects.get(usuario=request.user)

    if request.method == 'GET' and estudiante:
        matriculas = Matricula.objects.filter(estudiante=estudiante).all()
        preinscripciones_examen = PreinscripcionExamen.objects.filter(persona=estudiante)
        calificaciones_examen = CalificacionExamen.objects.filter(preinscripcion_examen__in=preinscripciones_examen)
        context = {'matriculas': matriculas, 'calificaciones_examen': calificaciones_examen}

    return render(request, template_name, context)


@login_required
def cursoCalificacionesDetalle(request, matricula, opcion):

    template_name = 'administracion/historiaAcademica/curso_calificaciones_detail.html'
    context = {}
    try:
        matricula_encontrada = Matricula.objects.get(pk=matricula)
    except Matricula.DoesNotExist:
        matricula_encontrada = None

    if request.method == 'GET' and matricula:

        tipo_general = TipoDocente.objects.get(tipo='General')
        tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
        docentes_generales = DocentesGrupoAcademico.objects.filter(grupo_academico=matricula_encontrada.grupo,tipo_docente=tipo_general).all()
        docentes_especializados = DocentesGrupoAcademico.objects.filter(grupo_academico=matricula_encontrada.grupo, tipo_docente=tipo_especializado).all()
        docentes = {docente.docente.persona: docente.tipo_docente for docente in docentes_generales}
        for docente in docentes_especializados:
            if docente not in docentes:
                docentes[docente.docente.persona] = docente.tipo_docente
        salones = matricula_encontrada.grupo.salones.all()
        enlace_virtual = matricula_encontrada.grupo.enlace_virtual

        calificaciones = Calificacion.objects.filter(matricula=matricula_encontrada).order_by('nota__orden_nota_conjunto').all()
        observaciones = Observacion.objects.filter(matricula=matricula_encontrada).all()
        inasistencias = FallaAsistencia.objects.filter(matricula=matricula_encontrada).order_by('fecha').all()

        context = {'matricula': matricula_encontrada, 'calificaciones': calificaciones,
                   'docentes_generales': docentes_generales, 'docentes_especializados': docentes_especializados, 'salones': salones,
                   'enlace_virtual': enlace_virtual, 'observaciones': observaciones, 'inasistencias': inasistencias, 'opcion': opcion, 'docentes': docentes}

    return render(request, template_name, context)


@login_required
def cursoCalificacionesDetallePDF(request, matricula, opcion):

    template_name = 'administracion/historiaAcademica/curso_calificaciones_detail.html'
    context = {}
    try:
        matricula_encontrada = Matricula.objects.get(pk=matricula)
    except Matricula.DoesNotExist:
        matricula_encontrada = None

    if request.method == 'GET' and matricula:

        tipo_general = TipoDocente.objects.get(tipo='General')
        tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
        docentes_generales = DocentesGrupoAcademico.objects.filter(grupo_academico=matricula_encontrada.grupo,tipo_docente=tipo_general).all()
        docentes_especializados = DocentesGrupoAcademico.objects.filter(grupo_academico=matricula_encontrada.grupo, tipo_docente=tipo_especializado).all()
        docentes = {docente.docente.persona: docente.tipo_docente for docente in docentes_generales}
        for docente in docentes_especializados:
            if docente not in docentes:
                docentes[docente.docente.persona] = docente.tipo_docente
        salones = matricula_encontrada.grupo.salones.all()

        calificaciones = Calificacion.objects.filter(matricula=matricula_encontrada).order_by('nota__orden_nota_conjunto').all()
        observaciones = Observacion.objects.filter(matricula=matricula_encontrada).all()
        inasistencias = FallaAsistencia.objects.filter(matricula=matricula_encontrada).order_by('fecha').all()

        context = {'matricula': matricula_encontrada, 'calificaciones': calificaciones,
                   'docentes_generales': docentes_generales, 'docentes_especializados': docentes_especializados, 'salones': salones,
                   'observaciones': observaciones, 'inasistencias': inasistencias, 'opcion': opcion, 'docentes': docentes}

        return funcion(context)

    return render(request, template_name, context)