from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, ListView, DeleteView
from django.shortcuts import render, redirect
from django.db.models import Q

from django.urls import reverse_lazy
from administracion.forms.autorizarForm import AutorizadoForm, AutorizadoLoteForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from administracion.models import Autorizado, ProgramaAcademico, OfertaAcademica, Curso, HorarioCurso, Profile, Periodo, \
    TipoDocumentoIdentidad, AutorizadoCurso
from django.contrib import messages
import json, datetime

from administracion.views.busqueda_list import BusquedaGenerica
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required

class AutorizadoCreate(LoginRequiredMixin, CreateView):
    form_class = AutorizadoForm
    template_name = 'administracion/autorizado/autorizado_form.html'
    fields = '__all__'

@login_required
def autorizadosCursoList(request):
    
    campos = ['tipo_documento__nombre',
              'numero_documento',
              'periodo__alias',
              'motivo',
              'curso_autorizado__nombre',
              'horario_curso_autorizado__nombre',
              'autorizado_por__primer_nombre',
              'autorizado_por__segundo_nombre',
              'autorizado_por__primer_apellido',
              'autorizado_por__segundo_apellido',
              'estado',
              ]

    busqueda_generica = BusquedaGenerica()
    object_list = AutorizadoCurso.objects.filter(curso_autorizado__oferta_academica__periodo__activo=True)
    query_string = request.GET.get('q')

    if query_string:
        consulta = busqueda_generica.get_query(query_string, campos)
        object_list = object_list.filter(consulta).order_by('numero_documento')

    page = request.GET.get('page')
    paginator = Paginator(object_list, 20)
    try:
        autorizados = paginator.page(page)
    except PageNotAnInteger:
        autorizados = paginator.page(1)
    except EmptyPage:
        autorizados = paginator.page(paginator.num_pages)

    return render(request, 'administracion/autorizado/autorizado_list.html', {'object_list': autorizados, 'total': len(object_list)})

@login_required
def escogerOpcionAutorizado(request):

    return render(request, 'administracion/autorizado/autorizado_opciones.html')

def buscarAutorizadoCurso(numero_documento, tipoDocumento, curso, periodo_id):

    idioma = None
    try:
        curso = Curso.objects.get(pk=curso)
    except Curso.DoesNotExist:
        curso = None

    if curso:
        idioma = curso.nivel.idioma

    autorizado = AutorizadoCurso.objects.filter(Q(curso_autorizado_id=curso) | Q(curso_autorizado__nivel__idioma=idioma), numero_documento=numero_documento, tipo_documento_id = tipoDocumento, estado__in=[1,2], periodo__id=periodo_id).all()
    return autorizado

@login_required
def autorizadoCreateView(request):

    periodo_id = request.session["periodo_contextualizado_id"]
    periodo = Periodo.objects.get(pk=periodo_id)
    hoy = timezone.now()

    if request.method == 'GET':
        form = AutorizadoForm(instance=None)
    else:
        form = AutorizadoForm(request.POST)

        if form.is_valid():
            curso_id = request.POST['curso']
            horario_curso = request.POST['horario_curso']
            autoriza = Profile.objects.get(pk=request.user.profile.id)
            numero_documento = form.data['numero_documento'].strip()
            tipo_documento = form.data['tipo_documento']
            autorizados_encontrados = buscarAutorizadoCurso(numero_documento, tipo_documento, curso_id, periodo_id)
            curso = Curso.objects.get(pk=curso_id)

            if len(autorizados_encontrados) > 0:
                messages.add_message(request, messages.WARNING, 'ERROR: La persona con documento ' + numero_documento + ' ya se encuentra autorizada a un curso del mismo idioma en el periodo ' + periodo.nombreAmigable())
                return render(request, 'administracion/autorizado/autorizado_opciones.html', {'form': form})

            autorizado = form.save(commit=False)
            autorizado.periodo_id = periodo_id
            autorizado.curso_autorizado_id = curso_id
            horario_curso_autorizado = None
            if horario_curso != '':
                horario_curso_autorizado = horario_curso
            autorizado.horario_curso_autorizado_id = horario_curso_autorizado
            autorizado.autorizado_por = autoriza
            autorizado.fecha_hora_autorizacion = hoy
            autorizado.save()

            messages.add_message(request, messages.SUCCESS, 'Se ha registrado el autorizado con documento ' + numero_documento
                    + ' al curso: ' + curso.nombre)

        return redirect('autorizado_opciones')

    return render(request, 'administracion/autorizado/autorizado_form.html', {'form': form,
                                                                              'periodo': periodo})

@login_required
def autorizadoUpdate(request, pk):

    template_name = 'administracion/autorizado/autorizado_form.html'
    instance = AutorizadoCurso.objects.get(pk = pk)
    periodo_id = instance.periodo.id
    hoy = timezone.now()
    horario_curso_inicial = instance.horario_curso_autorizado

    if request.method == "GET":

        if instance.estado == 2:
            messages.add_message(request, messages.WARNING, 'La persona que escogió NO puede ser modificada porque ya usó el cupo')
            return redirect('autorizado_opciones')

        tipo_documento = instance.tipo_documento
        numero_documento = instance.numero_documento
        motivo = instance.motivo
        curso = None
        try:
            curso = Curso.objects.get(pk=instance.curso_autorizado_id)
        except IntegrityError:
            messages.error(request, 'Hubo un error al mostrar el autorizado por la inexistencia del curso')

        if instance.horario_curso_autorizado_id != None:
            horario_curso_inicial = HorarioCurso.objects.get(pk = instance.horario_curso_autorizado_id)
        programa = curso.oferta_academica.programa
        periodo = curso.oferta_academica.periodo
        idioma = curso.nivel.idioma

        programas_academicos = ProgramaAcademico.objects.filter(idioma=idioma.id, activo=True).exclude(pk = programa.id).order_by('nombre').all()
        ofertas_academicas = OfertaAcademica.objects.filter(periodo_id=periodo_id, programa=programa.id).all()
        cursos = Curso.objects.filter(oferta_academica__in=ofertas_academicas).order_by('nombre').all()
        horarios = HorarioCurso.objects.filter(curso_id = curso.id).order_by('nombre').all()
        cursos = cursos.exclude(pk=curso.id)

        mostrar_horarios = False
        if horario_curso_inicial != None:
            horarios = horarios.exclude(pk=horario_curso_inicial.id)
        else:
            mostrar_horarios = True

        initial = {'tipo_documento': tipo_documento, 'numero_documento': numero_documento,
                  'motivo': motivo,'idioma': idioma.id}

        form = AutorizadoForm(initial=initial)
        return render(request, template_name, {'form':form, 'periodo': periodo, 'programa': programa,
                                               'curso': curso, 'horario_curso': horario_curso_inicial,
                                               'programas_academicos': programas_academicos,
                                               'cursos': cursos,
                                               'horarios': horarios,
                                               'mostrar_horarios': mostrar_horarios})
    else:
        form = AutorizadoForm(request.POST)

        if form.is_valid():
            curso_id = request.POST['curso']
            horario_curso = request.POST['horario_curso']
            autoriza = Profile.objects.get(pk=request.user.profile.id)
            numero_documento = request.POST['numero_documento'].strip()
            tipo_documento = request.POST['tipo_documento']
            motivo = request.POST['motivo']

            autorizado_curso = buscarAutorizadoCurso(numero_documento, tipo_documento, curso_id, periodo_id)
            ids = [autorizado.id for autorizado in autorizado_curso]
            if len(autorizado_curso) > 0 and instance.id not in ids:
                messages.add_message(request, messages.WARNING,
                                     'La persona con documento ' +  numero_documento + ' ya se encuentra autorizada a un curso del mismo idioma')
                return redirect('autorizado_opciones')

            instance.tipo_documento = TipoDocumentoIdentidad.objects.get(pk=tipo_documento)
            instance.numero_documento = numero_documento
            instance.periodo_id = periodo_id
            instance.motivo = motivo
            instance.curso_autorizado_id = curso_id

            if horario_curso == '':
                instance.horario_curso_autorizado_id = None
            else:
                instance.horario_curso_autorizado_id = horario_curso

            instance.autorizado_por = autoriza
            instance.fecha_hora_autorizacion = hoy
            instance.save()

            messages.add_message(request, messages.SUCCESS,'Se ha modificado la persona autorizada')

            return redirect('autorizado_opciones')

@login_required
def autorizadoLoteView(request):

    periodo_id = request.session["periodo_contextualizado_id"]
    periodo = Periodo.objects.get(pk=periodo_id)
    campos = 'Tipo_documento_identidad,Numero_documento'
    tipos_documento = TipoDocumentoIdentidad.objects.values_list('nombre', flat=True)
    ERROR = 'ERROR'
    EXITO = 'EXITO'
    hoy = timezone.now()
    cupos_autorizados = 0

    if request.method == 'GET':
        form = AutorizadoLoteForm()
    else:
        form = AutorizadoLoteForm(request.POST, request.FILES)
        if form.is_valid():
            curso_id = request.POST['curso']
            curso = Curso.objects.get(pk=curso_id)
            horario_curso = request.POST['horario_curso']
            motivo = request.POST['motivo']
            autoriza = Profile.objects.get(pk=request.user.profile.id)
            file_data = None
            try:
                archivo = request.FILES['archivo']

                if not archivo.name.endswith('.csv'):
                    messages.error(request, 'El archivo debe tener la extensión .csv')

                file_data = archivo.read().decode("utf-8")

            except Exception as e:
                messages.warning(request, "Ocurrio un error al leer el archivo " + repr(e))

            lines = file_data.split('\n')

            i = 1
            data_dict = {}
            documentos = []
            data_dict[0] = ['tipo_documento', 'documento', 'curso', 'horario', 'resultado']

            for line in lines:
                horario = ''
                if line != '' and len(line.split(",")) > 1:
                    fields = line.split(",")
                    message = EXITO + ': Guardado_exitoso'
                    tipo_doc = fields[0].upper()
                    if tipo_doc not in tipos_documento:
                        message = ERROR + ': El_tipo_documento_' + fields[0] + '_no_es_valido'
                    else:
                        tipo_documento = TipoDocumentoIdentidad.objects.get(nombre=tipo_doc).id
                        numero_documento = fields[1].strip()
                        if numero_documento != '':
                            autorizados_encontrados = buscarAutorizadoCurso(numero_documento, tipo_documento, curso_id, periodo_id)

                            if len(autorizados_encontrados) > 0:
                                message = ERROR + ': Autorizado_al_mismo_idioma_ya_existe_en_el_periodo_actual'
                            else:
                                if numero_documento not in documentos:
                                    autorizado = AutorizadoCurso()
                                    autorizado.tipo_documento_id = tipo_documento
                                    autorizado.numero_documento = numero_documento
                                    autorizado.periodo_id = periodo_id
                                    autorizado.motivo = motivo
                                    autorizado.curso_autorizado_id = curso_id

                                    horario_curso_autorizado = None
                                    if horario_curso != '':
                                        horario_curso_autorizado = horario_curso

                                    autorizado.horario_curso_autorizado_id = horario_curso_autorizado
                                    autorizado.autorizado_por = autoriza
                                    autorizado.fecha_hora_autorizacion = hoy
                                    autorizado.save()

                                    cupos_autorizados += 1
                                    documentos.append(numero_documento)
                                else:
                                    message = 'ERROR: ' + 'Documento_' + numero_documento + '_repetido_en_el_archivo'
                        else:
                            message = 'ERROR: ' + 'Campo_documento_vacio '
                    data_dict[i] = [fields[0], fields[1], curso.nombre, horario, message]

                else:
                    message = ERROR + ': La_linea' + str(i) + '_no_tiene_el_formato_requerido'
                    data_dict[i] = [line, '', '', '', message]

                i = i + 1

            # Guardar los autorizados
            data_dict = json.dumps(data_dict)
            messages.add_message(request, messages.SUCCESS,
                                 'Se han autorizado a ' + str(cupos_autorizados) + ' personas al curso: ' + curso.nombre)
            return render(request,
                          'administracion/cargaEnLote/resultado_lote.html', {'resultado': data_dict, 'tipo': 'curso'})

    return render(request, 'administracion/autorizado/autorizado_lote.html', {'form': form,
                                                                              'periodo': periodo,
                                                                              'campos': campos,
                                                                              'tipos_documento': tipos_documento})

class AutorizadoDelete(LoginRequiredMixin, DeleteView):
    model = AutorizadoCurso
    template_name = 'administracion/autorizado/autorizado_confirm_delete.html'
    success_url = reverse_lazy('autorizados')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        autorizado_curso_id = self.object.id

        try:
            autorizado_curso = AutorizadoCurso.objects.get(pk=autorizado_curso_id)
        except AutorizadoCurso.DoesNotExist:
            autorizado_curso = None

        if autorizado_curso:
            if autorizado_curso.estado == 2:
                messages.add_message(request, messages.WARNING, 'La persona que escogió NO puede ser eliminada porque ya usó el cupo')
                return redirect('autorizado_opciones')
            messages.add_message(request, messages.SUCCESS,
                                 'Se ha borrado la autorización para el persona con documento ' + autorizado_curso.numero_documento + ' en el curso: ' + autorizado_curso.curso_autorizado.nombre)

            autorizado_curso.delete()
        return HttpResponseRedirect(self.get_success_url())

@login_required
def cargar_programas_academicos_autorizado(request):
    if request.user.is_authenticated:
        idioma_id = request.GET.get('idioma')
        if idioma_id != '':
            programas_academicos = ProgramaAcademico.objects.filter(idioma = idioma_id, activo=True).order_by('nombre').all()
            data={}
            for i in programas_academicos:
                data[str(i.id)]=i.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def cargar_cursos_autorizado(request):

    if request.user.is_authenticated:
        data = {}
        periodo_id = request.session["periodo_contextualizado_id"]
        programa_id = request.GET.get('programa_academico')
        if programa_id != '':
            ofertas_academicas = OfertaAcademica.objects.filter(periodo_id = periodo_id, programa=programa_id).all()
            cursos = Curso.objects.filter(oferta_academica__in=ofertas_academicas).all().order_by('nivel__orden')
            for curso in cursos:
                data[str(curso.id)] = curso.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})

    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def cargar_horarios_autorizado(request):
    if request.user.is_authenticated:
        curso_id = request.GET.get('curso')
        if curso_id != '':
            try:
                curso = Curso.objects.get(pk = curso_id)
            except Curso.DoesNotExist:
                curso = None
            horarios = HorarioCurso.objects.filter(curso=curso).order_by('nombre').all()
            data = {}
            for horario in horarios:
                data[str(horario.id)] = horario.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})
