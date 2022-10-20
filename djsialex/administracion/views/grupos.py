from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Max
from django.contrib import messages

from administracion.util import CSVWriter
from administracion.views import BusquedaGenerica
from ..models import GrupoAcademico, OfertaAcademica, HorarioCurso, Curso, PreinscripcionHorarioCurso, Matricula, \
    DocentesGrupoAcademico, TipoDocente, Docente, Salon, ESTADOS_ACADEMICOS_MATRICULA, getEstadoMatricula, \
    ContenidoNivel, ContenidoNivelVersion, Nivel
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.views.generic.edit import CreateView
from ..forms import GrupoAcademicoForm, CambioGrupoForm, AsignarSalonDocenteAGrupoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalDeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def getPreinscritosPorCurso(horario_curso):
    preinscritos_horario_curso = PreinscripcionHorarioCurso.objects.filter(horario_cupo_id=horario_curso.id, estado_preinscripcion__in=[1,3]).all() #estados: Inscrito, Pendiente
    return preinscritos_horario_curso


def getInscritosSinMatricula(inscritos, horario_curso):
    estudiantes = inscritos.values_list('persona_id', flat=True)
    matriculados = Matricula.objects.filter(estudiante__in=estudiantes, grupo__horarioCurso__curso=horario_curso.curso).values_list('estudiante_id',flat=True)
    inscritos_sin_matricula = inscritos.exclude(persona__in = matriculados)
    return inscritos_sin_matricula

def guardarGruposYMatriculas(grupos, horario_curso):

    errores = ''
    try:
        grupo_estudiante = Group.objects.get(name='Estudiante')
    except GrupoAcademico.DoesNotExist:
        grupo_estudiante = None

    for gr in grupos:
        nombre_grupo = grupos[gr][0]
        preinscritos = grupos[gr][1]
        grupo = GrupoAcademico(nombre=nombre_grupo, horarioCurso_id=horario_curso.id)
        grupo_encontrado = GrupoAcademico.objects.filter(nombre=nombre_grupo)
        if len(grupo_encontrado) == 0:
            contenido_nivel = horario_curso.curso.nivel.contenido
            if contenido_nivel:
                version_contenido = ContenidoNivelVersion.objects.filter(contenido_nivel=contenido_nivel).aggregate(max=Max('version'))['max']
                ultima_version_contenido = ContenidoNivelVersion.objects.filter(contenido_nivel=contenido_nivel, version=version_contenido).first()
                grupo.contenido_nivel_version = ultima_version_contenido
            grupo.save()

            matriculas = []
            for preinscrito in preinscritos:
                matricula = Matricula(estudiante=preinscrito.persona, grupo=grupo,
                                      estado_matricula=7)  # Estado: En curso
                matricula_encontrada = Matricula.objects.filter(estudiante=preinscrito.persona, grupo=grupo,
                                                                estado_matricula=7)
                if not matricula_encontrada and matricula not in matriculas:
                    matriculas.append(matricula)
            try:
                with transaction.atomic():
                    Matricula.objects.bulk_create(matriculas)
            except IntegrityError:
                errores += ' , No se pudieron guardar las matriculas'

            if grupo_estudiante:
                for matricula in matriculas:
                    estudiante = matricula.estudiante
                    if grupo_estudiante not in estudiante.usuario.groups.all():
                        estudiante.usuario.groups.add(grupo_estudiante)
        else:
            errores += ' , El grupo con nombre ' + nombre_grupo + ' ya existe'
    return errores

def asignarGrupoAPreinscritos(numero_grupos, preinscritos_curso, horario_curso):

    errores = ''
    nombre_curso = horario_curso.curso.nivel.nombre + '-' + horario_curso.curso.nivel.idioma.nombre + '-' + horario_curso.horario.nombre + '-' + horario_curso.curso.oferta_academica.periodo.alias
    len_preinscritos = len(preinscritos_curso)

    grupos_existentes = GrupoAcademico.objects.filter(horarioCurso_id=horario_curso.id)
    inicio_grupos = 0
    fin_grupos = numero_grupos +  1

    if len(grupos_existentes) > 0:
        for grupo in grupos_existentes:
            numero_grupo = int(grupo.nombre.split('-')[1])
            if numero_grupo > inicio_grupos:
                inicio_grupos = numero_grupo
        fin_grupos = inicio_grupos + numero_grupos + 1

    inicio_grupos += 1

    grupos = {num_grupo : ['GRU-' + str(num_grupo) + '-' + nombre_curso, []] for num_grupo in range(inicio_grupos,fin_grupos)}
    preinscritos_list = list(preinscritos_curso)
    if len_preinscritos >= numero_grupos and numero_grupos > 0:
        personas_por_grupo = int(len_preinscritos / numero_grupos)
        if personas_por_grupo > 0:
            g = inicio_grupos
            inicio = 0
            fin = personas_por_grupo - 1
            resto = len(preinscritos_curso) % numero_grupos
            numero_grupos += inicio_grupos - 1
            while g <= numero_grupos:
                personas = preinscritos_list[inicio: fin+1]
                inicio = fin + 1
                fin = inicio + personas_por_grupo -1
                grupos[g][1] = personas
                g += 1
            if resto != 0:
                g = inicio_grupos
                personas = preinscritos_list[-resto:]
                for p in personas:
                    persona_grupo = grupos[g][1]
                    if p not in persona_grupo:
                        persona_grupo.append(p)
                        g += 1
            errores += guardarGruposYMatriculas(grupos, horario_curso)
    else:
        errores += '.El número de inscritos sin matrícula debe ser mayor al número de grupos a crear'
    return errores

def get_matriculas_numero(grupo):
    conteo = 0
    grupos = GrupoAcademico.objects.annotate(numero_de_matriculas=Count('matricula'))
    for grupo_anotado in grupos:
        if grupo_anotado.id == grupo.id:
            conteo = grupo_anotado.numero_de_matriculas
    return conteo

@login_required
def seleccionOfertaAcademica(request, template_name='administracion/grupos/seleccionar_oferta.html'):
    if request.GET:
        oferta_filtrada = request.GET['oferta']
        ofertas = OfertaAcademica.objects.filter(periodo_id= request.session["periodo_contextualizado_id"])
        current_oferta = request.GET['oferta']
        cursos = Curso.objects.filter(oferta_academica_id=oferta_filtrada).order_by("nivel__orden")
        niveles_curso = {}
        grupos_matriculas = {}
        for curso in cursos:
            horarios_cursos = HorarioCurso.objects.filter(curso=curso).order_by("nombre")
            niveles_curso[curso] = {}
            for horario_curso in horarios_cursos:
                grupos = GrupoAcademico.objects.filter(horarioCurso_id=horario_curso.id).all().order_by("nombre")
                inscritos = getPreinscritosPorCurso(horario_curso)
                niveles_curso[curso][horario_curso] = [len(inscritos), len(getInscritosSinMatricula(inscritos, horario_curso)), grupos]#horario_curso.cupo_inicial - horario_curso.cupo_disponible + horario_curso.cupo_autorizados - horario_curso.cupo_disponible_autorizados
                for grupo in grupos:
                    grupos_matriculas[grupo] = get_matriculas_numero(grupo)
        context_dict = {'niveles_curso': niveles_curso, 'ofertas': ofertas, 'current_oferta': current_oferta, 'grupos_matriculas' : grupos_matriculas}
    else:
        ofertas = OfertaAcademica.objects.filter(periodo_id= request.session["periodo_contextualizado_id"])
        context_dict = {'ofertas': ofertas}

    return render(request, template_name, context_dict)


@login_required
@csrf_exempt
def asignarGrupos(request, template_name = 'administracion/grupos/seleccionar_oferta.html'):

    errores = ''
    if request.method == 'POST':
        horarios_curso_grupos = request.POST.get('json_data')
        horarios_curso_grupos = json.loads(horarios_curso_grupos)
        for dict in horarios_curso_grupos:
            horario_curso_id = dict['horario_curso']
            numero_grupos = dict['numero_grupos'].strip()
            try:
                horario_curso = HorarioCurso.objects.get(pk=horario_curso_id)
            except HorarioCurso.DoesNotExist:
                horario_curso = None
            if horario_curso and numero_grupos.isdigit():
                numero_grupos = int(numero_grupos)
                preinscritos_curso = getPreinscritosPorCurso(horario_curso)
                inscritos_sin_matricula = getInscritosSinMatricula(preinscritos_curso, horario_curso)
                if numero_grupos > len(inscritos_sin_matricula):

                    errores += 'El número de inscritos sin matrícula debe ser mayor al número de grupos a crear.' \
                               ' Revise qué valor debe corregir.'
                    break
                elif len(inscritos_sin_matricula) > 0:
                    asignarGrupoAPreinscritos(numero_grupos, inscritos_sin_matricula, horario_curso)

        if errores != '':
            response = HttpResponse(errores, status=401)
            response['Content-Length'] = len(response.content)
            return response
        else:
            return HttpResponseRedirect(request.path_info)
    return render(request, template_name)


class GrupoAcademicoCreateView(LoginRequiredMixin,CreateView):
    template_name = 'administracion/grupos/grupo_form.html'
    form_class = GrupoAcademicoForm
    success_message = 'Nuevo Grupo creado.'

    def get(self, request, *args, **kwargs):
        data = dict()
        horariocurso = HorarioCurso.objects.get(id=self.kwargs['horariocurso'])
        grupos_existentes = GrupoAcademico.objects.filter(horarioCurso_id=horariocurso.id)
        len_grupos = len(grupos_existentes)
        fecha_inicio = horariocurso.curso.oferta_academica.periodo.fecha_inicio
        fecha_final = horariocurso.curso.oferta_academica.periodo.fecha_final
        if fecha_inicio is None or fecha_final is None:
            fecha_inicio = date.today()
            fecha_final = date.today()
        nombre_curso = horariocurso.curso.nivel.nombre + '-' + horariocurso.curso.nivel.idioma.nombre + '-' + horariocurso.horario.nombre + '-' + horariocurso.curso.oferta_academica.periodo.alias
        grupo_nombre = 'GRU-' + str(len_grupos+1) + '-' + nombre_curso
        form = GrupoAcademicoForm(
            initial={'nombre': grupo_nombre, 'horarioCurso': horariocurso, 'fecha_inicio': fecha_inicio,
                     'fecha_final': fecha_final}
        )
        context = {'form': form, 'horariocurso': horariocurso.id}
        data['html_form'] = render_to_string('administracion/grupos/grupo_form.html', context, request=request)
        return JsonResponse(data)

    def form_valid(self, form):
        context = self.get_context_data()
        grupo_form = context['form']
        if grupo_form.is_valid():
            return super(GrupoAcademicoCreateView,self).form_valid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('seleccion_oferta')


@login_required
def cambiarGrupo(request, nivel):
    periodo = request.session["periodo_contextualizado_id"]
    template_name = 'administracion/grupos/cambiar_grupo_form.html'
    grupos = GrupoAcademico.objects.filter(horarioCurso__curso__nivel_id=nivel, estado=0, horarioCurso__curso__oferta_academica__periodo_id = periodo )
    try:
        nivel = Nivel.objects.get(pk=nivel)
    except Nivel.DoesNotExist:
        nivel = None
    current_grupo1 = None
    current_grupo2 = None
    if request.GET.get('grupo1') and request.GET.get('grupo2'):
        grupo1_filtrado = request.GET['grupo1']
        current_grupo1 = grupo1_filtrado
        grupo2_filtrado = request.GET['grupo2']
        current_grupo2 = grupo2_filtrado
        matriculas_grupo2 = Matricula.objects.filter(grupo_id=current_grupo2, estado_matricula__in=[1,2,7])
        form = CambioGrupoForm(grupo1_filtrado)
        context_dict = {"grupo": grupo1_filtrado, "form" : form, 'nivel' : nivel, 'grupos' : grupos, 'current_grupo1' : current_grupo1, 'current_grupo2' : current_grupo2, 'matriculas_grupo2' : matriculas_grupo2}
    elif request.method == "GET":
        context_dict = {'grupos': grupos, 'nivel': nivel, 'current_grupo1': current_grupo1,
                        'current_grupo2': current_grupo2}
    elif request.method == "POST":
        matriculas = request.POST.getlist("matriculas")
        if matriculas:
            for m in matriculas:
                try:
                    matricula_cambio = Matricula.objects.get(pk=m)
                except Matricula.DoesNotExist:
                    matricula_cambio = None
                if matricula_cambio:
                    matricula_cambio.grupo_id = request.POST.get("grupoDestino")
                    matricula_cambio.save()
        return redirect('seleccion_oferta')
    return render(request, template_name, context_dict)

# Delete
class GrupoAcademicoDeleteView(BSModalDeleteView):
    model = GrupoAcademico
    template_name = 'administracion/grupos/grupo_delete.html'
    success_message = 'Grupo borrado.'
    success_url = reverse_lazy('seleccion_oferta')

@login_required
def matriculaPorGrupoAcademicoList(request, grupoacademico):

        campos = ['grupo__codigo',
                  'estudiante__numero_documento',
                  'estudiante__primer_nombre',
                  'estudiante__segundo_nombre',
                  'estudiante__primer_apellido',
                  'estudiante__segundo_apellido',
                  'grupo__horarioCurso__nombre',
                  'grupo__codigo'
                  ]

        try:
            grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
        except GrupoAcademico.DoesNotExist:
            grupo_academico = None

        if grupo_academico:
            DATE_FORMAT = "%d-%m-%Y"
            fecha_inicio = grupo_academico.fecha_inicio.strftime("%s" % (DATE_FORMAT)) if grupo_academico.fecha_inicio else None
            fecha_final = grupo_academico.fecha_final.strftime("%s" % (DATE_FORMAT)) if grupo_academico.fecha_final else None
            enlace_virtual = grupo_academico.enlace_virtual
            docentes = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico).all()
            salones = grupo_academico.salones.all()

            busqueda_generica = BusquedaGenerica()
            object_list = Matricula.objects.filter(grupo=grupo_academico).order_by('estudiante__primer_apellido')
            query_string = request.GET.get('q')

            if query_string and grupo_academico:
                consulta = busqueda_generica.get_query(query_string, campos)
                object_list = Matricula.objects.filter(consulta).order_by('estudiante__primer_apellido').filter(grupo=grupo_academico)

            page = request.GET.get('page')
            paginator = Paginator(object_list, 1000)

            try:
                matriculas = paginator.page(page)
            except PageNotAnInteger:
                matriculas = paginator.page(1)
            except EmptyPage:
                matriculas = paginator.page(paginator.num_pages)

            return render(request, 'administracion/grupos/matriculas_por_grupo.html',
                          {'object_list': matriculas, 'grupo': grupo_academico, 'docentes': docentes,
                           'salones': salones, 'fecha_inicio': fecha_inicio, 'fecha_final': fecha_final,
                           'enlace_virtual': enlace_virtual, 'total': len(object_list)})

        return redirect('seleccion_oferta')

@login_required
def descargarListaPorGrupo(request, grupoacademico):

    try:
        grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo_academico = None

    matriculas = Matricula.objects.filter(grupo=grupo_academico).order_by('estudiante__primer_apellido').all()

    data = {i+1: [str(matriculas[i].grupo.codigo) , (matriculas[i].estudiante.getApellidos() + ' ' + matriculas[i].estudiante.getNombres()).upper(),
             matriculas[i].grupo.horarioCurso.curso.oferta_academica.periodo.alias , matriculas[i].grupo.horarioCurso.nombre ,
             matriculas[i].estudiante.numero_documento, getEstadoMatricula(matriculas[i].estado_matricula)]
             for i in range(len(matriculas))}

    header = ['#','codigo-grupo', 'Nombre estudiante','Periodo','Curso','Documento','Estado']

    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, str(grupo_academico.codigo))
    return response

@login_required
def informacionDocenteSalonAGrupo(request, grupoacademico):
    campos = ['grupo__codigo',
                'estudiante__numero_documento',
                'estudiante__primer_nombre',
                'estudiante__segundo_nombre',
                'estudiante__primer_apellido',
                'estudiante__segundo_apellido',
                'grupo__horarioCurso__nombre',
                'grupo__codigo'
                ]
                
    try:
        grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo_academico = None

    if grupo_academico:

        docentes = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico).all()
        salones = grupo_academico.salones.all()

        busqueda_generica = BusquedaGenerica()
        object_list = Matricula.objects.filter(grupo=grupo_academico).order_by('estudiante__primer_apellido')
        query_string = request.GET.get('q')

        if query_string and grupo_academico:
            consulta = busqueda_generica.get_query(query_string, campos)
            object_list = Matricula.objects.filter(consulta).order_by('estudiante__primer_apellido').filter(grupo=grupo_academico)

        page = request.GET.get('page')
        paginator = Paginator(object_list, 1000)

        try:
            matriculas = paginator.page(page)
        except PageNotAnInteger:
            matriculas = paginator.page(1)
        except EmptyPage:
            matriculas = paginator.page(paginator.num_pages)

    tipo_general = TipoDocente.objects.get(tipo='General')
    tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
    context = {}
    try:
        grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo_academico = None

    if request.method == 'GET':
        docentes_generales_actual = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico, tipo_docente=tipo_general).all().order_by('docente__persona__primer_apellido', 'docente__persona__primer_nombre')
        docentes_especializados_actual = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico, tipo_docente=tipo_especializado).all().order_by('docente__persona__numero_documento', 'docente__persona__primer_nombre')
        form = AsignarSalonDocenteAGrupoForm(grupo_academico.id)

        salones = grupo_academico.salones.all()
        observaciones = grupo_academico.observaciones
        context = {'docentes_generales_actual': docentes_generales_actual, 'docentes_especializados_actual': docentes_especializados_actual,
                   'salones_asignados': salones, 'grupo': grupo_academico, 'observaciones': observaciones, 'form': form}

    return render(request, 'administracion/grupos/correoGrupo.html',
                {'object_list': matriculas, 'grupo': grupo_academico, 'docentes': docentes,
                'salones': salones, 'total': len(object_list)})


@login_required
def asignarDocenteSalonAGrupo(request, grupoacademico):

    tipo_general = TipoDocente.objects.get(tipo='General')
    tipo_especializado = TipoDocente.objects.get(tipo='Especializado')
    context = {}
    try:
        grupo_academico = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo_academico = None

    if request.method == 'GET':
        DATE_FORMAT = "%d-%m-%Y"
        docentes_generales_actual = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico, tipo_docente=tipo_general).all().order_by('docente__persona__primer_apellido', 'docente__persona__primer_nombre')
        docentes_especializados_actual = DocentesGrupoAcademico.objects.filter(grupo_academico=grupo_academico, tipo_docente=tipo_especializado).all().order_by('docente__persona__numero_documento', 'docente__persona__primer_nombre')
        form = AsignarSalonDocenteAGrupoForm(grupo_academico.id)

        salones = grupo_academico.salones.all()
        observaciones = grupo_academico.observaciones
        codigo_proyecto = grupo_academico.codigo_proyecto
        fecha_inicio = grupo_academico.fecha_inicio.strftime("%s" % (DATE_FORMAT)) if grupo_academico.fecha_inicio else None
        fecha_final = grupo_academico.fecha_final.strftime("%s" % (DATE_FORMAT)) if grupo_academico.fecha_final else None
        enlace_virtual = grupo_academico.enlace_virtual
        context = {'docentes_generales_actual': docentes_generales_actual,
                   'docentes_especializados_actual': docentes_especializados_actual,
                   'salones_asignados': salones, 'grupo': grupo_academico, 'observaciones': observaciones,
                   'codigo_proyecto': codigo_proyecto,
                   'fecha_inicio': fecha_inicio, 'fecha_final': fecha_final,
                   'enlace_virtual': enlace_virtual, 'form': form}

    elif request.method == 'POST':

        form = AsignarSalonDocenteAGrupoForm(grupoacademico, request.POST)

        if form.is_valid():
            docentes_generales = request.POST.getlist('docentes_generales')
            docentes_especializados = request.POST.getlist('docentes_especializados')
            salones = request.POST.getlist('salones')
            observaciones = request.POST.get('observaciones')
            codigo_proyecto = request.POST.get('codigo_proyecto')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_final = request.POST.get('fecha_final')
            enlace_virtual = request.POST.get('enlace_virtual')

            for docente_id in docentes_generales:
                docente_general = DocentesGrupoAcademico(docente_id=docente_id, grupo_academico=grupo_academico, tipo_docente=tipo_general)
                docente_general.save()

            for docente_id in docentes_especializados:
                docente_especializado = DocentesGrupoAcademico(docente_id=docente_id, grupo_academico=grupo_academico, tipo_docente=tipo_especializado)
                docente_especializado.save()

            for salon in salones:
                try:
                    salon_grupo = Salon.objects.get(pk=salon)
                except Salon.DoesNotExist:
                    salon_grupo = None
                if salon_grupo and salon_grupo not in grupo_academico.salones.all():
                    grupo_academico.salones.add(salon_grupo)

            grupo_academico.observaciones = str(observaciones).strip()
            grupo_academico.codigo_proyecto = str(codigo_proyecto).strip()
            grupo_academico.fecha_inicio = fecha_inicio if fecha_inicio else None
            grupo_academico.fecha_final = fecha_final if fecha_final else None
            grupo_academico.enlace_virtual = enlace_virtual
            grupo_academico.save()

        return redirect('grupo-detail', grupoacademico=grupoacademico)

    return render(request, 'administracion/grupos/asignar_docente_salon.html', context)


@login_required
def eliminarSalonDeGrupo(request, grupoacademico, salon):

    try:
        salon_grupo = Salon.objects.get(pk=salon)
    except Salon.DoesNotExist:
        salon_grupo = None

    try:
        grupo = GrupoAcademico.objects.get(pk=grupoacademico)
    except GrupoAcademico.DoesNotExist:
        grupo = None

    if salon_grupo and grupo:

        grupo.salones.remove(salon_grupo)
        grupo.save()

    return redirect('grupo-detail', grupoacademico=grupoacademico)

@login_required
def eliminarDocenteDeGrupo(request, grupoacademico, docente):

    try:
        docente_grupo = DocentesGrupoAcademico.objects.get(pk=docente)
    except DocentesGrupoAcademico.DoesNotExist:
        docente_grupo = None

    if docente_grupo:
        docente_grupo.delete()

    return redirect('grupo-detail', grupoacademico=grupoacademico)


@login_required
def verPreinscritosCurso(request, horario_curso):

    preinscripciones = None

    if request.method == 'GET':

        try:
            curso = HorarioCurso.objects.get(pk=horario_curso)
        except HorarioCurso.DoesNotExist:
            curso = None


        if curso:

            preinscripciones = PreinscripcionHorarioCurso.objects.filter(horario_cupo=curso).order_by('persona__primer_nombre', 'fecha_preinscripcion').all()

        return render(request, 'administracion/grupos/preinscritos_horario_curso.html',
                          {'preinscripciones': preinscripciones, 'horario_curso': curso})

    return render(request, 'administracion/grupos/preinscritos_horario_curso.html',
                  {'preinscripciones': preinscripciones})


@login_required
def verPreinscritosSinMatriculaCurso(request, horario_curso):

    preinscripciones = None

    if request.method == 'GET':

        try:
            curso = HorarioCurso.objects.get(pk=horario_curso)
        except HorarioCurso.DoesNotExist:
            curso = None


        if curso:
            inscritos = getPreinscritosPorCurso(curso)

            preinscripciones = getInscritosSinMatricula(inscritos, curso)

        return render(request, 'administracion/grupos/preinscritos-sin-matricula.html',
                          {'preinscripciones': preinscripciones, 'horario_curso': curso})

    return render(request, 'administracion/grupos/preinscritos-sin-matricula.html',
                  {'preinscripciones': preinscripciones})