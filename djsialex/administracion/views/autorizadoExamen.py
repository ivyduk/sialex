from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, ListView, DeleteView
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.urls import reverse_lazy
from administracion.forms.autorizarForm import AutorizadoForm, AutorizadoLoteForm, AutorizadoExamenForm, \
    AutorizadoExamenLoteForm
from administracion.models import Autorizado, ProgramaAcademico, OfertaAcademica, Curso, HorarioCurso, Profile, Periodo, \
    TipoDocumentoIdentidad, AutorizadoCurso, AutorizadoExamen, ExamenClasificacion
from django.contrib import messages
import json, datetime

from administracion.views.busqueda_list import BusquedaGenerica
from django.utils import timezone
from django.db import IntegrityError, transaction


def autorizadoExamenCreateView(request):
    periodo_id = request.session["periodo_contextualizado_id"]
    periodo = Periodo.objects.get(pk=periodo_id)
    hoy = timezone.now()

    if request.method == 'GET':
        form = AutorizadoExamenForm(instance=None)
    else:
        form = AutorizadoExamenForm(request.POST)

        if form.is_valid():
            examen_id = request.POST['examen']
            autoriza = Profile.objects.get(pk=request.user.profile.id)
            numero_documento = form.data['numero_documento'].strip()
            tipo_documento = form.data['tipo_documento']
            autorizados_encontrados = buscarAutorizadoExamen(numero_documento, tipo_documento, examen_id)

            try:
                examen = ExamenClasificacion.objects.get(pk=examen_id)
            except ExamenClasificacion.DoesNotExist:
                examen = None

            if examen:
                if len(autorizados_encontrados) > 0:
                    messages.add_message(request, messages.WARNING,
                                     'ERROR: La persona con documento ' + numero_documento + ' ya se encuentra autorizada al examen ' + examen.nombre + ' en el periodo ' + periodo.nombreAmigable())
                    return render(request, 'administracion/autorizado/autorizado_opciones.html', {'form': form})


                autorizado = form.save(commit=False)
                autorizado.periodo_id = periodo_id
                autorizado.examen_id = examen_id
                autorizado.autorizado_por = autoriza
                autorizado.fecha_hora_autorizacion = hoy
                autorizado.save()

                messages.add_message(request, messages.SUCCESS,
                                 'Se ha registrado el autorizado con documento ' + numero_documento
                                 + ' al curso: ' + examen.nombre)
            else:
                messages.add_message(request, messages.WARNING,
                                     'ERROR: El examen seleccionado no existe en el periodo ' + periodo.nombreAmigable())
                return render(request, 'administracion/autorizado/autorizado_opciones.html', {'form': form})

        return redirect('autorizado_opciones')

    return render(request, 'administracion/autorizado/autorizadoExamen/autorizado_examen_form.html', {'form': form,
                                                                              'periodo': periodo})

def autorizadoExamenLoteView(request):

    periodo_id = request.session["periodo_contextualizado_id"]
    periodo = Periodo.objects.get(pk=periodo_id)
    campos = 'Tipo_documento_identidad,Numero_documento'
    tipos_documento = TipoDocumentoIdentidad.objects.values_list('nombre', flat=True)
    ERROR = 'ERROR'
    EXITO = 'EXITO'
    hoy = timezone.now()
    cupos_autorizados = 0

    if request.method == 'GET':
        form = AutorizadoExamenLoteForm()
    else:
        form = AutorizadoExamenLoteForm(request.POST, request.FILES)
        if form.is_valid():
            examen_id = request.POST['examen']
            try:
                examen = ExamenClasificacion.objects.get(pk = examen_id)
            except ExamenClasificacion.DoesNotExist:
                examen = None

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

            if examen:
                i = 1
                data_dict = {}
                documentos = []
                data_dict[0] = ['tipo_documento', 'documento', 'examen', 'resultado']

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
                            autorizados_encontrados = buscarAutorizadoExamen(numero_documento, tipo_documento, examen_id)

                            if len(autorizados_encontrados) > 0:
                                message = ERROR + ': Autorizado_a_examen_ya_existe_en_el_periodo_actual'
                            else:
                                if numero_documento not in documentos:
                                    autorizado = AutorizadoExamen()
                                    autorizado.tipo_documento_id = tipo_documento
                                    autorizado.numero_documento = numero_documento
                                    autorizado.periodo_id = periodo_id
                                    autorizado.motivo = motivo
                                    autorizado.examen_id = examen_id
                                    autorizado.autorizado_por = autoriza
                                    autorizado.fecha_hora_autorizacion = hoy
                                    autorizado.save()

                                    cupos_autorizados += 1
                                    documentos.append(numero_documento)
                                else:
                                    message = 'ERROR: ' + 'Documento_' + numero_documento + '_repetido_en_el_archivo'

                        data_dict[i] = [fields[0], fields[1], examen.nombre, message]

                    else:
                        message = ERROR + ': La_linea' + str(i) + '_no_tiene_el_formato_requerido'
                        data_dict[i] = [line, '', '', '', message]

                    i = i + 1

                # Guardar los autorizados
                data_dict = json.dumps(data_dict)
                messages.add_message(request, messages.SUCCESS,
                                 'Se han autorizado a ' + str(cupos_autorizados) + ' personas al examen: ' + examen.nombre)
                return render(request,
                              'administracion/cargaEnLote/resultado_lote.html', {'resultado': data_dict, 'tipo': 'examen'})
            else:
                messages.add_message(request, messages.ERROR, 'El examen es inválido')
                return render(request, 'administracion/autorizado/autorizado_opciones.html')

    return render(request, 'administracion/autorizado/autorizadoExamen/autorizado_examen_lote.html', {'form': form,
                                                                              'periodo': periodo,
                                                                              'campos': campos,
                                                                              'tipos_documento': tipos_documento})

@login_required
def autorizadosExamenList(request):
    campos = ['tipo_documento__nombre',
              'numero_documento',
              'periodo__alias',
              'motivo',
              'examen__nombre',
              'autorizado_por__primer_nombre',
              'autorizado_por__segundo_nombre',
              'autorizado_por__primer_apellido',
              'autorizado_por__segundo_apellido',
              'estado',
              ]
    busqueda_generica = BusquedaGenerica()
    object_list = AutorizadoExamen.objects.filter(examen__periodo__activo=True)
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

    return render(request, 'administracion/autorizado/autorizadoExamen/autorizado_examen_list.html', {'object_list': autorizados, 'total': len(object_list)})

def buscarAutorizadoExamen(numero_documento, tipoDocumento, examen):

    autorizado = AutorizadoExamen.objects.filter(numero_documento=numero_documento, tipo_documento_id = tipoDocumento, examen_id=examen).all()
    return autorizado

@login_required
def cargar_examenes_autorizado(request):

    if request.user.is_authenticated:
        idioma_id = request.GET.get('idioma')
        if idioma_id != '':
            periodo_id = request.session["periodo_contextualizado_id"]
            examenes_clasificacion = ExamenClasificacion.objects.filter(idioma = idioma_id, periodo_id = periodo_id, cupo_disponible_autorizado__gt=0).order_by('nombre').all()
            data={}
            for i in examenes_clasificacion:
                data[str(i.id)]=i.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

class AutorizadoExamenDelete(LoginRequiredMixin, DeleteView):

    model = AutorizadoExamen
    template_name = 'administracion/autorizado/autorizadoExamen/autorizado_examen_confirm_delete.html'
    success_url = reverse_lazy('autorizados-examen')
    paginate_by = 20

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        autorizado_examen_id = self.object.id

        try:
            autorizado_examen = AutorizadoExamen.objects.get(pk=autorizado_examen_id)
        except AutorizadoExamen.DoesNotExist:
            autorizado_examen = None

        if autorizado_examen:
            if autorizado_examen.estado == 2:
                messages.add_message(request, messages.WARNING, 'La persona que escogió NO puede ser eliminada porque ya usó el cupo')
                return redirect('autorizado_opciones')
            messages.add_message(request, messages.SUCCESS,
                                 'Se ha borrado la autorización para el persona con documento ' + autorizado_examen.numero_documento + ' en el examen: ' + autorizado_examen.examen.nombre)

            autorizado_examen.delete()
        return HttpResponseRedirect(self.get_success_url())