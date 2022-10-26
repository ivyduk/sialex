import collections

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from administracion.models import Profile, Docente, GrupoAcademico, Matricula, Periodo, NotaParcial, Calificacion, \
    DocentesGrupoAcademico, TipoDocente, FallaAsistencia, usuarioTieneGrupo, Observacion, getEstadoMatricula, \
    PreinscripcionHorarioCurso, OfertaAcademica
import json

from administracion.util import CSVWriter


def isDocente(user):
    persona = Profile.objects.filter(usuario__id = user.id).first()
    return Docente.objects.filter(persona__id = persona.id).exists()

@login_required
def cursosAsociadosList(request):

    user = request.user
    es_administrador = usuarioTieneGrupo(user, 'Administrador') or usuarioTieneGrupo(user, 'Coordinador')

    periodo_actual_id = request.session["periodo_contextualizado_id"]
    try:
        periodo = Periodo.objects.get(pk=periodo_actual_id)
    except Periodo.DoesNotExist:
        periodo = None
    context = {}
    mis_cursos = collections.OrderedDict()

    if request.method == 'GET':
        persona = Profile.objects.filter(usuario__id=user.id).first()
        docentes = Docente.objects.filter(persona__id=persona.id)

        if len(docentes) > 0 or es_administrador:

            if es_administrador:
                grupos = GrupoAcademico.objects.filter(horarioCurso__curso__oferta_academica__periodo=periodo).order_by('horarioCurso__curso__nivel__idioma__nombre', 'horarioCurso__curso__nivel__nombre')
            else:
                grupos = GrupoAcademico.objects.filter(docentesgrupoacademico__docente__in=docentes, horarioCurso__curso__oferta_academica__periodo=periodo).order_by('horarioCurso__curso__nivel__idioma__nombre', 'horarioCurso__curso__nivel__nombre')
            for grupo in grupos:
                curso = grupo.horarioCurso.curso
                # Matriculas: Se excluyen aquellas que estan canceladas o aplazadas por usuario y departamento
                matriculas = Matricula.objects.filter(grupo=grupo).exclude(estado_matricula__in=[4,5,6]).all()
                if curso not in mis_cursos:
                    mis_cursos[curso] = []
                mis_cursos[curso].append([grupo, len(matriculas)])
            context = {'mis_cursos': mis_cursos, 'periodo': periodo}

        else:
            messages.warning(request, 'Lo sentimos, a usted no le ha sido asignado el rol de docente.'
                             'Por favor comuníquese con el administrador del sistema')

    return render(request, "administracion/docente/mis_cursos_list.html", context)

@login_required
def listadoEstudiantesPorGrupo(request, grupoacademico):

    context = {}
    user = request.user
    persona = Profile.objects.filter(usuario__id=user.id).first()
    docentes = Docente.objects.filter(persona__id=persona.id)
    tipo_general = TipoDocente.objects.get(tipo='General')
    tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
    periodo_actual = request.session["periodo_contextualizado_id"]
    tipo_docente = None
    es_administrador = False
    observaciones = {}

    if request.method == 'GET':
        try:
            grupo = GrupoAcademico.objects.get(pk=grupoacademico)
        except GrupoAcademico.DoesNotExist:
            grupo = None

        try:
            periodo = Periodo.objects.get(pk=periodo_actual)
        except Periodo.DoesNotExist:
            periodo = None

        if grupo and periodo:
            #Matriculas: Se excluyen aquellas que estan canceladas o aplazadas por usuario y departamento
            matriculas = Matricula.objects.filter(grupo=grupo).exclude(estado_matricula__in=[4,5,6]).order_by('estudiante__primer_apellido', 'estudiante__segundo_apellido')
            escala_notas = grupo.horarioCurso.curso.oferta_academica.programa.escala_nota
            docentes_generales = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, tipo_docente=tipo_general).all()
            docentes_especializados = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, tipo_docente=tipo_especializado).all()

            docente = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, docente__in=docentes).first()
            salones = grupo.salones.all()

            if docente:
                tipo_docente = docente.tipo_docente
            if usuarioTieneGrupo(user, 'Administrador'):
                es_administrador = True

            for matricula in matriculas:
                observaciones[matricula] = len(Observacion.objects.filter(matricula=matricula))

            context = {'matriculas': matriculas, 'periodo': periodo, 'grupo': grupo,
                       'escala_notas': escala_notas,
                       'docentes_generales': docentes_generales, 'docentes_especializados': docentes_especializados,
                       'tipo_docente': tipo_docente, 'es_administrador': es_administrador,
                       'salones': salones, 'observaciones_matricula': observaciones}

    return render(request, "administracion/docente/mis_estudiantes_list.html", context)


@login_required
def listadoCalificacionesPorGrupo(request, grupoacademico):

    context = {}
    user = request.user
    persona = Profile.objects.filter(usuario__id=user.id).first()
    docentes = Docente.objects.filter(persona__id=persona.id)
    tipo_general = TipoDocente.objects.get(tipo='General')
    tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
    periodo_actual = request.session["periodo_contextualizado_id"]
    tipos_docente = None
    es_administrador_o_coordinador = False

    if request.method == 'GET':
        try:
            grupo = GrupoAcademico.objects.get(pk=grupoacademico)
        except GrupoAcademico.DoesNotExist:
            grupo = None

        try:
            periodo = Periodo.objects.get(pk=periodo_actual)
        except Periodo.DoesNotExist:
            periodo = None

        if grupo and periodo:
            calificaciones_matricula = {}
            #Matriculas: Se excluyen aquellas que estan canceladas o aplazadas por usuario y departamento
            preinscripcion = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion__in=[1, 3, 5],
                                                                     horario_cupo__curso__oferta_academica__periodo  = OuterRef('grupo__horarioCurso__curso__oferta_academica__periodo'),
                                                                     horario_cupo__curso__oferta_academica__programa = OuterRef('grupo__horarioCurso__curso__oferta_academica__programa'),
                                                                     horario_cupo__curso__nivel                      = OuterRef('grupo__horarioCurso__curso__nivel'),
                                                                     persona                                         = OuterRef('estudiante')
                                                                    )

            matriculas = Matricula.objects.filter(grupo=grupo
                                                ).exclude(estado_matricula__in=[4,5,6]).order_by('estudiante__primer_apellido'
                                                ).annotate(estado_preinscripcion = Subquery(preinscripcion.values('estado_preinscripcion')))
            
            for matricula in matriculas:
                calificaciones = Calificacion.objects.filter(matricula=matricula).all()
                if matricula not in calificaciones_matricula:
                    calificaciones_matricula[matricula] = {}
                for calificacion in calificaciones:
                    nota_parcial = calificacion.nota
                    calificaciones_matricula[matricula][nota_parcial] = calificacion.calificacion

            conjunto_notas = grupo.horarioCurso.curso.conjunto_notas
            notas = NotaParcial.objects.filter(conjunto_notas=conjunto_notas).order_by('orden_nota_conjunto').all()
            escala_notas = grupo.horarioCurso.curso.oferta_academica.programa.escala_nota
            docentes_generales = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, tipo_docente=tipo_general).all()
            docentes_especializados = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, tipo_docente=tipo_especializado).all()

            docentes = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo, docente__in=docentes).all()

            if docentes:
                tipos_docente = [docente.tipo_docente.id for docente in docentes]
                #tipo_docente = docente.tipo_docente
            if usuarioTieneGrupo(user, 'Administrador') or usuarioTieneGrupo(user, 'Coordinador'):
                es_administrador_o_coordinador = True

            context = {'matriculas': matriculas, 'periodo': periodo, 'grupo': grupo, 'notas': notas, 'range': range(len(notas)),
                       'calificaciones_matricula': calificaciones_matricula, 'escala_notas': escala_notas,
                       'docentes_generales': docentes_generales, 'docentes_especializados': docentes_especializados,
                       'tipos_docente': tipos_docente, 'es_administrador': es_administrador_o_coordinador}

    return render(request, "administracion/docente/matriculas_list.html", context)

def asignarCalificacion(matricula_nota, nota_parcial, calificacion, escala_notas):

    errores = ''
    try:
        calificacion_nota = float(calificacion)
    except:
        calificacion_nota = 0.0

    try:
        calificacion_encontrada = Calificacion.objects.get(matricula=matricula_nota, nota=nota_parcial)
    except Calificacion.DoesNotExist:
        calificacion_encontrada = None

    if calificacion_nota > escala_notas.nota_maxima:
        return 'La calificación debe ser menor o igual a ' + str(escala_notas.nota_maxima) + ' para el estudiante: ' + str(matricula_nota.estudiante.numero_documento)
    elif calificacion_nota < escala_notas.nota_minima:
        return 'La calificación debe ser mayor igual a ' + str(escala_notas.nota_minima) + ' para el estudiante: ' + str(matricula_nota.estudiante.numero_documento)

    if calificacion_encontrada:

        calificacion_encontrada.calificacion = calificacion_nota
        calificacion_encontrada.save()
    else:
        calificacion = Calificacion(matricula=matricula_nota, nota=nota_parcial, calificacion=calificacion_nota)
        calificacion.save()

    return errores

def asignarCalificacionFinal(matricula_nota, escala_notas):

    calificaciones_matricula = Calificacion.objects.filter(matricula=matricula_nota).all()
    calificacion_final = 0.0
    for calificacion in calificaciones_matricula:
        calificacion_final += calificacion.calificacion * calificacion.nota.ponderacion / 100
    matricula_nota.calificacionFinal = round(calificacion_final, escala_notas.numero_decimales)
    matricula_nota.save()

@login_required
@csrf_exempt
def calificarGrupo(request, grupoacademico):

    errores = ''
    if request.method == 'POST':
        estudiantes = request.POST.get('json_data')
        estudiantes = json.loads(estudiantes)
        count_calificaciones = 0

        try:
            grupo = GrupoAcademico.objects.get(pk=grupoacademico)
        except:
            grupo = None

        if grupo:

            escala_notas = grupo.horarioCurso.curso.oferta_academica.programa.escala_nota

            for estudiante in estudiantes:
                for matricula in estudiante:

                    try:
                        matricula_nota = Matricula.objects.get(pk=matricula)
                    except:
                        matricula_nota = None

                    for nota in estudiante[matricula]:
                        calificacion = estudiante[matricula][nota]

                        try:
                            nota_parcial = NotaParcial.objects.get(pk=nota)
                        except:
                            nota_parcial = None

                        if matricula_nota and nota_parcial:

                            errores += asignarCalificacion(matricula_nota, nota_parcial, calificacion, escala_notas)

                    count_calificaciones += 1
                    asignarCalificacionFinal(matricula_nota, escala_notas)

        status = 1
        message = 'Se han guardado las calificaciones de ' + str(len(estudiantes)) + ' estudiantes del grupo: ' + grupo.nombre

        if errores != '':
            status = 0
            message = (errores)

        response = {'status': status, 'message': message}
        return HttpResponse(json.dumps(response), content_type='application/json')

    return render(request, 'administracion/docente/mis_cursos_list.html')

def actualizarEstadoMatriculasPorGrupo(grupo_academico, ofertas_periodo):

    matriculas = Matricula.objects.filter(grupo=grupo_academico).all()
    curso = grupo_academico.horarioCurso.curso
    numero_maximo_fallas = curso.nivel.fallas_maximas
    nota_aprobatoria = curso.oferta_academica.programa.escala_nota.nota_aprobatoria

    for matricula in matriculas:
        fallas = FallaAsistencia.objects.filter(matricula=matricula).aggregate(Sum('cantidad_fallas'))['cantidad_fallas__sum']

        try:
            preinscripcion_asociada = PreinscripcionHorarioCurso.objects.get(persona=matricula.estudiante,
                                                                         horario_cupo__curso=matricula.grupo.horarioCurso.curso,
                                                                         estado_preinscripcion__in=[1,3],
                                                                         horario_cupo__curso__oferta_academica__in=ofertas_periodo)  # Inscrito o Pendiente
        except PreinscripcionHorarioCurso.DoesNotExist:
            preinscripcion_asociada = None

        if fallas:
            matricula.total_fallas = fallas

        if matricula.estado_matricula not in [4, 5, 6]:  # Cancelado, Aplazado por usuario, Aplazado por departamento
            if matricula.total_fallas > numero_maximo_fallas:
                matricula.estado_matricula = 8  # Reprobado por inasistencia
            else:
                matricula.estado_matricula = 7  # en curso

        if matricula.estado_matricula not in [8, 4, 5, 6]:
            if matricula.calificacionFinal < nota_aprobatoria:
                matricula.estado_matricula = 3  # Reprobado por calificación
            elif preinscripcion_asociada  and preinscripcion_asociada.estado_preinscripcion == 2:  # Pendiente
                matricula.estado_matricula = 9  # Aprobado - Pendiente en Formalizacion
            elif preinscripcion_asociada and preinscripcion_asociada.estado_preinscripcion == 1:  # Inscrito
                matricula.estado_matricula = 2  # Aprobado

        matricula.save()

@login_required
def actualizarEstadoMatriculasGrupos(request):

    periodo = request.session["periodo_contextualizado_id"]
    if request.method == 'GET':
        ofertas_academicas = OfertaAcademica.objects.filter(periodo_id=periodo)
        grupos = GrupoAcademico.objects.filter(horarioCurso__curso__oferta_academica__in=ofertas_academicas)
        for grupo in grupos:
            actualizarEstadoMatriculasPorGrupo(grupo, ofertas_academicas)

    return redirect(request.META['HTTP_REFERER'])

@login_required
def actualizarEstadoMatriculas(request, grupoacademico):

    periodo = request.session["periodo_contextualizado_id"]
    if request.method == 'GET':
        ofertas_academicas = OfertaAcademica.objects.filter(periodo_id=periodo)
        grupo = GrupoAcademico.objects.get(pk=grupoacademico)
        actualizarEstadoMatriculasPorGrupo(grupo, ofertas_academicas)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def descargarNotasPorGrupo(request, grupoacademico):

    try:
        grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo_academico = None

    # Matriculas: Se excluyen aquellas que estan canceladas o aplazadas por usuario y departamento
    matriculas = Matricula.objects.filter(grupo=grupo_academico).exclude(estado_matricula__in=[4,5,6]).order_by('estudiante__primer_apellido').all()
    observaciones = {}

    for matricula in matriculas:
        observaciones[matricula] = len(Observacion.objects.filter(matricula=matricula))

    data = {i+1: [str(matriculas[i].grupo.codigo) ,
                  matriculas[i].estudiante.numero_documento,
                  (matriculas[i].estudiante.getApellidos() + ' ' + matriculas[i].estudiante.getNombres()).upper(),
                  matriculas[i].estudiante.usuario.email,
                  matriculas[i].grupo.horarioCurso.curso.oferta_academica.periodo.alias,
                  matriculas[i].grupo.horarioCurso.nombre,
                  str(matriculas[i].calificacionFinal),
                  getEstadoMatricula(matriculas[i].estado_matricula),
                  str(matriculas[i].total_fallas),
                  str(observaciones[matriculas[i]])]
             for i in range(len(matriculas))}

    header = ['#','codigo-grupo', 'Documento','Nombre estudiante','Correo electronico','Periodo','Curso','Nota final','Estado', '# Inasistencias', '# Observaciones']

    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, str(grupo_academico.codigo) + '-Calificaciones')
    return response

@login_required
def descargarNotasGrupos(request):

    ofertas_academicas = OfertaAcademica.objects.filter(periodo__id=request.session['periodo_contextualizado_id'])
    grupos_academicos = GrupoAcademico.objects.filter(horarioCurso__curso__oferta_academica__in=ofertas_academicas).order_by('horarioCurso__curso__nivel__idioma__nombre', 'horarioCurso__curso__nivel__nombre')

    data = {}
    i = 1
    for grupo_academico in grupos_academicos:
        # Matriculas: Se excluyen aquellas que estan canceladas o aplazadas por usuario y departamento
        matriculas = Matricula.objects.filter(grupo=grupo_academico).exclude(estado_matricula__in=[4,5,6]).order_by('estudiante__primer_apellido').all()
        observaciones = {}

        for matricula in matriculas:
            observaciones[matricula] = len(Observacion.objects.filter(matricula=matricula))

            data[i] = [str(matricula.grupo.codigo) ,
                  matricula.estudiante.numero_documento,
                  (matricula.estudiante.getApellidos() + ' ' + matricula.estudiante.getNombres()).upper(),
                  matricula.estudiante.usuario.email,
                  matricula.grupo.horarioCurso.curso.oferta_academica.periodo.alias,
                  matricula.grupo.horarioCurso.nombre,
                  str(matricula.calificacionFinal),
                  getEstadoMatricula(matricula.estado_matricula),
                  str(matricula.total_fallas),
                  str(observaciones[matricula])]

            i += 1

    header = ['#','codigo-grupo', 'Documento','Nombre estudiante','Correo electronico','Periodo','Curso','Nota final','Estado', '# Inasistencias', '# Observaciones']

    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, 'Calificaciones')
    return response