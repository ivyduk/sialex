from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json
import hashlib
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from itertools import chain

from administracion.forms.inscripcionForm import PreinscripcionCursoForm, PreinscripcionCursoLoteForm
from administracion.forms.requiereFacturacionForms import RequiereFacturacionForm

from administracion.util.Barcode import *
from ..models import PreinscripcionHorarioCurso, ProgramaAcademico, Nivel, OfertaAcademica, Curso, HorarioCurso, \
    Profile, \
    Descuento, Periodo, Autorizado, Idioma, ReciboPreinscripcion, AutorizadoCurso, Preinscripcion, PreinscripcionExamen, \
    AutorizadoExamen, DescuentoAplicado, DocumentosDescuentoSolicitado, Beca, Pago, ComprobanteBanco, \
    CalificacionExamen, TipoDocumentoIdentidad, Matricula, SaldoAFavor, ReservasSaldo, \
    InformacionPreinscripcionFormalizacion, GrupoAcademico, usuarioTieneGrupo

from datetime import datetime

from ..modules import AyudanteFinancieros, CalcularPagosRecibo, check_saldo_cargado
from django.contrib.auth.decorators import login_required

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.db.models import Q
from django.template import loader
from django.core.mail import send_mail


class CancelPreinscripcion(LoginRequiredMixin, DeleteView):

    model = Preinscripcion
    template_name = 'administracion/inscripcion/preinscripcion_confirm_delete.html'
    success_url = reverse_lazy('mis-preinscripciones')

    def get_success_url(self):
        if self.request.user.groups.filter(name="Funcionario").exists():
            return reverse_lazy('buscar-preinscripciones')
        else:
            return reverse_lazy('mis-preinscripciones')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        preinscripcion_id = self.object.id
        periodo_id = request.session["periodo_contextualizado_id"]
        try:
            preinscripcion = PreinscripcionHorarioCurso.objects.get(pk=preinscripcion_id)
        except PreinscripcionHorarioCurso.DoesNotExist:
            preinscripcion = None
        try:
            preinscrito = Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            preinscrito = None
        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            periodo = None

        if preinscrito and periodo:
            ayudante = AyudanteFinancieros(preinscrito, periodo)
            if preinscripcion and self.object: #curso
                ayudante.actualizar_financieros_cancelacion_preinscripcion_sin_pago(preinscripcion, True)
                try:
                    horario_cupo = HorarioCurso.objects.get(pk=preinscripcion.horario_cupo.id)
                    #buscar si es autorizado
                    autorizado_curso = AutorizadoCurso.objects.filter(numero_documento=preinscrito.numero_documento, periodo=periodo, curso_autorizado=horario_cupo.curso, estado=2).all().first()
                    if autorizado_curso:
                        horario_cupo.cupo_disponible_autorizados += 1
                        autorizado_curso.estado = 3 #cancelada
                        autorizado_curso.save()
                    else:
                        horario_cupo.cupo_disponible += 1
                    horario_cupo.save()
                except HorarioCurso.DoesNotExist:
                    pass
            elif self.object: #Examen
                preinscripcion = PreinscripcionExamen.objects.get(pk=self.object.id)
                ayudante.actualizar_financieros_cancelacion_preinscripcion_sin_pago(preinscripcion, False)
                examen = preinscripcion.examen
                autorizado_examen = AutorizadoExamen.objects.filter(numero_documento=preinscrito.numero_documento,
                                                                            periodo=periodo, examen=examen, estado=2).all().first()

                if autorizado_examen:
                    examen.cupo_disponible_autorizado += 1
                    autorizado_examen.estado = 3 #cancelada
                    autorizado_examen.save()
                else:
                    examen.cupo_disponible += 1
                examen.save()
            preinscripcion.estado_preinscripcion = 6 #Cancelado
            preinscripcion.save()
            try:
                recibo_preinscripcion = ReciboPreinscripcion.objects.get(preinscripcion=preinscripcion)
                recibo_preinscripcion.estado_recibo = 1
                recibo_preinscripcion.save()
            except ReciboPreinscripcion.DoesNotExist:
                pass
        return HttpResponseRedirect(self.get_success_url())

class PreinscripcionCursoListView(LoginRequiredMixin, generic.ListView):
    model = PreinscripcionHorarioCurso
    template_name = 'administracion/inscripcion/mis_inscripciones.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        perfil = Profile.objects.get(usuario=self.request.user)
        periodo_id = self.request.session["periodo_contextualizado_id"]
        preinscripcionesCurso = PreinscripcionHorarioCurso.objects.filter(persona=perfil, horario_cupo__curso__oferta_academica__periodo_id=periodo_id)
        preinscripcionesExamen = PreinscripcionExamen.objects.filter(persona=perfil, examen__periodo_id=periodo_id)
        return list(chain(preinscripcionesCurso, preinscripcionesExamen))

class PreinscripcionCursoCreate(LoginRequiredMixin, CreateView):
    model = PreinscripcionHorarioCurso
    form_class = PreinscripcionCursoForm
    template_name = 'administracion/inscripcion/preinscripcion_curso.html'

@login_required
def preinscripcionView(request):

    if request.method == 'GET':
        form = PreinscripcionCursoForm()
    else:
        form = PreinscripcionCursoForm(request.POST)
        idioma = request.POST['idioma']
        horario_curso = request.POST['horario_curso']
        descuento_id = request.POST['descuento']
        periodo_id = request.session["periodo_contextualizado_id"]
        hash_code = request.POST["hash"]
        if descuento_id:
            descuento = Descuento.objects.get(pk=descuento_id)
        else:
            descuento = None
        if form.is_valid():
            try:
                preinscrito = Profile.objects.get(pk = request.user.profile.id)
            except Profile.DoesNotExist:
                preinscrito = None
            try:
                horario = HorarioCurso.objects.get(pk=horario_curso)
            except HorarioCurso.DoesNotExist:
                horario = None
            try:
                periodo = Periodo.objects.get(pk=periodo_id)
            except Periodo.DoesNotExist:
                periodo = None

            if horario and horario.curso.nivel.mensaje_formalizacion:
                mensaje_formalizacion = horario.curso.nivel.mensaje_formalizacion
                documentos_mensaje = horario.curso.nivel.documentos_pago
            else:
                informacion_formalizacion = InformacionPreinscripcionFormalizacion.objects.get(periodo=periodo)
                mensaje_formalizacion = informacion_formalizacion.mensaje_formalizacion
                documentos_mensaje = informacion_formalizacion.documentos_pago

            if preinscrito and horario and periodo:

                ofertas_periodo = OfertaAcademica.objects.filter(periodo=periodo)
                oferta_horario = OfertaAcademica.objects.filter(periodo__activo=True,
                                                                periodo__finalizado=False)

                niveles = Nivel.objects.filter(idioma_id=idioma)
                preinscripcion_previa = PreinscripcionHorarioCurso.objects.filter(
                    estado_preinscripcion__in=[1, 3, 5],
                    horario_cupo__curso__nivel__in=niveles,
                    persona=preinscrito,
                    horario_cupo__curso__oferta_academica__in=ofertas_periodo
                ) #Estado 6: Cancelado
                preinscripcion_examen = PreinscripcionExamen.objects.filter(estado_preinscripcion__in=[1, 3, 5],
                                                                            persona=preinscrito,
                                                                            examen__periodo__activo=True,
                                                                            examen__periodo__finalizado=False,
                                                                            examen__idioma_id=idioma).first()
                preinscripcion_mismo_idioma = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion__in=[1,3,5],
                                                                                  horario_cupo__curso__nivel__in=niveles,
                                                                                  persona=preinscrito, horario_cupo__curso__oferta_academica__in=ofertas_periodo)
                preinscripcion_horario_existente = PreinscripcionHorarioCurso.objects.filter(
                    estado_preinscripcion__in=[1,3,5],
                    horario_cupo__horario=horario.horario,
                    horario_cupo__curso__oferta_academica__in=oferta_horario,
                    persona=preinscrito,
                    horario_cupo__curso__oferta_academica__periodo__fin__gt=periodo.inicio,
                    horario_cupo__curso__oferta_academica__periodo__inicio__lte=periodo.inicio,
                ).first()

                if not preinscripcion_previa and not preinscripcion_mismo_idioma and not preinscripcion_horario_existente and not preinscripcion_examen:
                    ayudante = AyudanteFinancieros(preinscrito, periodo)
                    tarifa_curso = horario.curso.oferta_academica.tarifa
                    valor_inscripcion, detallado_preinscripcion = ayudante.calcular_valor_preinscripcion_curso(tarifa_curso, horario.curso.nivel, descuento, horario.curso.nivel.costo_materiales)
                    #buscar si es autorizado
                    autorizado_curso = AutorizadoCurso.objects.filter(numero_documento=preinscrito.numero_documento, periodo=periodo, curso_autorizado=horario.curso, estado__in=[1,3]).all().first()
                    if autorizado_curso and horario.cupo_disponible_autorizados > 0:
                        if 'beca' in detallado_preinscripcion:
                            try:
                                beca = Beca.objects.get(pk=detallado_preinscripcion['beca']['id'])
                                beca.valor = float(detallado_preinscripcion['beca']['valor'])
                                beca.estado_beca = 2
                                beca.save()
                            except Beca.DoesNotExist:
                                beca = None
                        preinscripcion_curso = PreinscripcionHorarioCurso(persona=preinscrito, valor_preinscripcion = valor_inscripcion, codigo_hash=hash_code, horario_cupo = horario, descuento_solicitado=descuento)
                        preinscripcion_curso.save()
                        recibo = ReciboPreinscripcion.objects.create(preinscrito=preinscrito,preinscripcion=preinscripcion_curso, valor_requerido=tarifa_curso+horario.curso.nivel.costo_materiales, estado_recibo=2)
                        logger.info("Recibo preinscripción creado satisfactoriamente")
                        horario.cupo_disponible_autorizados = horario.cupo_disponible_autorizados -1
                        autorizado_curso.estado = 2 #completa
                        autorizado_curso.save()
                        horario.save()
                        if descuento:
                            documentos_requeridos = preinscripcion_curso.descuento_solicitado.documentos_requeridos.all()
                        else:
                            documentos_requeridos = []
                        # actualizar Financieros utilizados
                        ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                        logger.info("Financieros actualizados")

                        html_message = loader.render_to_string(
                            'administracion/inscripcion/preinscripcion_curso_confirmacion_email.html',
                            {
                                'preinscripcion_curso': preinscripcion_curso,
                                'documentos_requeridos': documentos_requeridos,
                                'detallado': detallado_preinscripcion,
                                'mensaje_formalizacion': mensaje_formalizacion,
                                'documentos_mensaje': documentos_mensaje
                            },
                            request=request
                        )
                        send_mail(
                            'Confirmación Preinscripción Curso',
                            '',
                            'sialex_fchbog@unal.edu.co',
                            [preinscrito.usuario.email],
                            fail_silently=True,
                            html_message=html_message
                        )

                        return render(
                            request,
                            'administracion/inscripcion/preinscripcion_curso_confirmacion.html',
                            {
                                'preinscripcion_curso': preinscripcion_curso,
                                'documentos_requeridos': documentos_requeridos,
                                'detallado': detallado_preinscripcion,
                                'mensaje_formalizacion': mensaje_formalizacion,
                                'documentos_mensaje': documentos_mensaje
                            }
                        )
                    elif horario.cupo_disponible > 0:
                        preinscripcion_curso = PreinscripcionHorarioCurso(persona=preinscrito,
                                                                          valor_preinscripcion=valor_inscripcion,
                                                                          codigo_hash=hash_code, horario_cupo=horario,
                                                                          descuento_solicitado=descuento)
                        preinscripcion_curso.save()
                        recibo = ReciboPreinscripcion.objects.create(preinscrito=preinscrito,
                                                                     preinscripcion=preinscripcion_curso,
                                                                     valor_requerido=tarifa_curso + horario.curso.nivel.costo_materiales,
                                                                     estado_recibo=2)
                        logger.info("Recibo preinscripción creado satisfactoriamente")
                        horario.cupo_disponible = horario.cupo_disponible - 1
                        horario.save()
                        if descuento:
                            documentos_requeridos = preinscripcion_curso.descuento_solicitado.documentos_requeridos.all()
                        else:
                            documentos_requeridos = []
                        # actualizar Financieros utilizados
                        ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                        logger.info("Financieros actualizados")

                        html_message = loader.render_to_string(
                            'administracion/inscripcion/preinscripcion_curso_confirmacion_email.html',
                            {
                                'preinscripcion_curso': preinscripcion_curso,
                                'documentos_requeridos': documentos_requeridos,
                                'detallado': detallado_preinscripcion,
                                'mensaje_formalizacion': mensaje_formalizacion,
                                'documentos_mensaje': documentos_mensaje
                            },
                            request=request
                        )
                        send_mail(
                            'Confirmación Preinscripción Curso',
                            '',
                            'sialex_fchbog@unal.edu.co',
                            [preinscrito.usuario.email],
                            fail_silently=True,
                            html_message=html_message
                        )
                        return render(
                            request,
                            'administracion/inscripcion/preinscripcion_curso_confirmacion.html',
                            {
                                'preinscripcion_curso': preinscripcion_curso,
                                'documentos_requeridos': documentos_requeridos,
                                'detallado': detallado_preinscripcion,
                                'mensaje_formalizacion': mensaje_formalizacion,
                                'documentos_mensaje': documentos_mensaje
                            }
                        )
                    else:
                        form.add_error('idioma', '¡Lo sentimos, la asignación de cupos ha finalizado! ')
                else:
                    if preinscripcion_previa:
                        form.add_error('idioma',
                                        'Ya existe una preinscripción para este usuario, en el mismo curso y horario. ')
                    if preinscripcion_mismo_idioma:
                        form.add_error('idioma', 'Ya existe una preinscripción para este idioma. ')
                    if preinscripcion_horario_existente:
                        form.add_error('idioma', 'Usted ya cuenta con una preinscripción en esta franja horaria. '
                                                    ' en el periodo: {}'.format(
                            preinscripcion_horario_existente.horario_cupo.curso.oferta_academica.periodo.alias
                        )
                                        )
                    if preinscripcion_examen:
                        form.add_error('idioma',
                                        'Usted ya cuenta con una preinscripcion para Examen de Calificación en este Idioma'
                                        ' en el periodo: {}'.format(
                                            preinscripcion_examen.examen.periodo.alias
                                        )
                                    )
    return render(request, 'administracion/inscripcion/preinscripcion_curso.html', {'form': form})


class PreinscripcionCursoUpdate(LoginRequiredMixin, UpdateView):

    model = PreinscripcionHorarioCurso
    template_name = 'administracion/inscripcion/cursos_opciones.html'
    fields = '__all__'

class PreinscripcionCursoDelete(LoginRequiredMixin, DeleteView):

    model = PreinscripcionHorarioCurso
    template_name = 'administracion/inscripcion/preinscripcion_confirm_delete.html'
    success_url = reverse_lazy('mis-inscripciones')

class PreinscripcionCursoDetailView(LoginRequiredMixin,generic.DetailView):
    model = PreinscripcionHorarioCurso
    template_name = 'administracion/inscripcion/preinscripcion_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(PreinscripcionCursoDetailView, self).get_context_data(**kwargs)
        preinscripcionhorariocurso = context['object']
        recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, preinscripcion=preinscripcionhorariocurso)
        context['tarifa_plena'] = recibopreinscripcion.valor_requerido - preinscripcionhorariocurso.horario_cupo.curso.nivel.costo_materiales
        descuento_aplicado = DescuentoAplicado.objects.filter(preinscripcion_generada=preinscripcionhorariocurso,
                                                              estado_descuento__in=(1, 2, 4))
        periodo_id = self.request.session["periodo_contextualizado_id"]
        periodo = Periodo.objects.get(pk=periodo_id)
        reservas_saldos = ReservasSaldo.objects.filter(preinscripcion_reserva=preinscripcionhorariocurso)
        try:
            mensaje_encontrado = InformacionPreinscripcionFormalizacion.objects.get(periodo=periodo)
            context['mensaje_formalizacion'] = mensaje_encontrado
        except InformacionPreinscripcionFormalizacion.DoesNotExist:
            mensaje_encontrado = None
        if reservas_saldos:
            context['reservas'] = reservas_saldos
        if descuento_aplicado:
            context['descuento_aplicado'] = descuento_aplicado[0]
        try:
            beca = Beca.objects.get(beneficiario=preinscripcionhorariocurso.persona,
                                    periodo_generado__inicio__gte=periodo.inicio - 4,
                                    nivel_idioma=preinscripcionhorariocurso.horario_cupo.curso.nivel)
        except Beca.DoesNotExist:
            beca = None
        try:
            matricula = Matricula.objects.get(estudiante=preinscripcionhorariocurso.persona, grupo__horarioCurso=preinscripcionhorariocurso.horario_cupo, estado_matricula__in=[1,2,3,7,8])
            grupo = matricula.grupo
        except Matricula.DoesNotExist:
            grupo = None
        context['grupo'] = grupo
        if beca:
            context['beca'] = beca
        return context


def calcularEdad(fechaNacimiento):

    fechaNacimiento = datetime.strptime(str(fechaNacimiento), "%Y-%m-%d")
    now = datetime.now()
    diferencia = now - fechaNacimiento

    return int((diferencia.days + diferencia.seconds/86400.0) / 365.2425)


def isAutorizacionNivelMenor():
    pass


@login_required()
def cargar_programas_academicos(request):
    error = False
    autorizaciones_dict = {}
    if request.user.is_authenticated:
        periodo_id = request.session["periodo_contextualizado_id"]
        idioma_id = request.GET.get('idioma')
        try:
            aspirante = Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            aspirante = None

        if aspirante:
            fecha_nacimiento = aspirante.fecha_nacimiento
            edad_aspirante = calcularEdad(fecha_nacimiento)
            programas_academicos = ProgramaAcademico.objects.filter(
                idioma_id=idioma_id,
                edad_minima__lte=edad_aspirante,
                edad_maxima__gt=edad_aspirante,
                activo=True,
                ofertaacademica__periodo__id=periodo_id
            ).order_by('nombre').all()

            if not programas_academicos:
                RejectedError = "ERROR|Usted no cuenta con la edad requerida para ningún Programa Académico disponible."

            if aspirante:
                autorizaciones = AutorizadoCurso.objects.filter(
                    numero_documento=aspirante.numero_documento,
                    periodo=periodo_id,
                    estado__in=[1, 3],
                    curso_autorizado__oferta_academica__programa__in=programas_academicos
                ).all() #Estado: AUTORIZADO o AUTORIZACIÓN CANCELADA
                for autorizacion in autorizaciones:
                    programa_autorizado = ProgramaAcademico.objects.filter(
                        pk=autorizacion.curso_autorizado.oferta_academica.programa.id
                    )
                    if autorizacion.curso_autorizado.id not in autorizaciones_dict:
                        autorizaciones_dict[str(autorizacion.curso_autorizado.id)] = str(autorizacion.horario_curso_autorizado_id) if autorizacion.horario_curso_autorizado_id else None
                        programas_academicos |= programa_autorizado
                request.session['autorizaciones_dict'] = autorizaciones_dict
        data = {}
        if programas_academicos:
            for i in programas_academicos:
                data[str(i.id)] = i.nombre
        else:
            data[str(id)] = RejectedError

        for i in programas_academicos:
            data[str(i.id)] = i.nombre
        serialized_obj = json.dumps(data)

        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required()
def cargar_niveles(request):
    if request.user.is_authenticated:

        try:
            aspirante = Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            aspirante = None

        edad_aspirante = 1

        if aspirante:
            fecha_nacimiento = aspirante.fecha_nacimiento
            edad_aspirante = calcularEdad(fecha_nacimiento)

        programa_academico_id = request.GET.get('programa_academico')
        programa_academico = ProgramaAcademico.objects.get(id=programa_academico_id)
        periodo_id = request.session["periodo_contextualizado_id"]
        periodo = Periodo.objects.get(pk=periodo_id)

        nivelesPre = Nivel.objects.none()

        # retornar niveles de ingreso orden=1
        niveles = ProgramaAcademico.objects.get(
            pk=programa_academico_id
        ).nivel.filter(
            activo=True,
            orden=1,
            edad_minima__lte=edad_aspirante,
            edad_maxima__gt=edad_aspirante
        ).all()

        if not niveles:
            RejectedError = "ERROR|Usted no cuenta con la edad requerida para los niveles disponibles."

        matriculas = Matricula.objects.filter(
            estudiante=request.user.profile,
            grupo__horarioCurso__curso__oferta_academica__periodo__inicio__gte=periodo.inicio-4,
            grupo__horarioCurso__curso__oferta_academica__programa_id=programa_academico_id
        )
        examenes_calificados_vigentes = CalificacionExamen.objects.filter(
            preinscripcion_examen__examen__periodo__inicio__gte=periodo.inicio-4,
            preinscripcion_examen__persona__id=aspirante.id,
            preinscripcion_examen__examen__idioma_id=programa_academico.idioma.id,
            nivel_id__isnull=False
        )
        if examenes_calificados_vigentes:
            for examen in examenes_calificados_vigentes:
                nivel_aprobado = Nivel.objects.filter(
                    orden=examen.nivel.orden,
                    idioma=examen.nivel.idioma
                )
                if nivel_aprobado:
                    nivelesPre |= nivel_aprobado
        if matriculas:
            for matricula in matriculas:
                if matricula.estado_matricula in (3, 4, 5, 6, 8):
                    nivel_reprobado = Nivel.objects.filter(id=matricula.grupo.horarioCurso.curso.nivel.id)
                    niveles |= nivel_reprobado
                elif matricula.estado_matricula == 2:
                    orden_superior = matricula.grupo.horarioCurso.curso.nivel.orden + 1
                    nivel_aprobado = Nivel.objects.filter(orden=orden_superior, idioma=matricula.grupo.horarioCurso.curso.nivel.idioma)
                    if nivel_aprobado:
                        nivelesPre |= nivel_aprobado
        autorizaciones_dict = request.session.get('autorizaciones_dict')
        for autorizacion in autorizaciones_dict:
            cursos_autorizado = Curso.objects.filter(pk=autorizacion).all()
            niveles_autorizado = Nivel.objects.filter(curso__in=cursos_autorizado).all().order_by('orden')

            if niveles_autorizado not in niveles:
                niveles |= niveles_autorizado

        if nivelesPre:
            niveles |= nivelesPre
        elif niveles:
            pass
        elif not nivelesPre:
            RejectedError = "ERROR|Usted no ha aprobado los NIVELES necesarios para preinscribirse a un NIVEL."


        niveles_aux = None

        if niveles:
            max_orden = 1
            for nivel in niveles:
                max_orden = nivel.orden if nivel.orden > max_orden else max_orden
                niveles_aux = niveles.exclude(orden__lt=max_orden)

        data = {}
        if niveles_aux:
            for i in niveles_aux:
                data[str(i.id)] = i.nombre
        else:
            data[str(id)] = RejectedError
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required()
def cargar_horarios_disponibles(request):
    if request.user.is_authenticated:
        nivel_id = request.GET.get('nivel')
        periodo_id = request.session["periodo_contextualizado_id"]
        periodo = Periodo.objects.get(pk=periodo_id)
        preinscrito = Profile.objects.get(pk=request.user.profile.id)

        # Validar si ya cuenta con una preinscripción a ese nivel en otro periodo
        nivel = Nivel.objects.get(pk=nivel_id)
        preinscripcion_mismo_idioma = PreinscripcionHorarioCurso.objects.filter(
            estado_preinscripcion__in=[1, 3, 5],
            horario_cupo__curso__nivel=nivel,
            persona=preinscrito,
            horario_cupo__curso__oferta_academica__periodo__inicio=periodo.inicio
        ).first()

        if preinscripcion_mismo_idioma:
           RejectedError = "ERROR|Ya cuenta con una preinscripción activa a este nivel en otro período."

        cursos = Curso.objects.filter(
            nivel=nivel_id,
            oferta_academica__periodo_id=periodo_id
        ).all()
        horarios = HorarioCurso.objects.filter(
            curso__in=cursos,
            cupo_disponible__gt=0
        ).order_by('nombre').all()

        if not horarios:
            RejectedError = "ERROR|No existen HORARIOS con cupos disponibles."

        autorizaciones_dict = request.session.get('autorizaciones_dict')
        cursos_ids = [str(curso) for curso in cursos.values_list('id', flat=True)]
        for autorizacion in autorizaciones_dict:
            if autorizacion in cursos_ids:
                if not autorizaciones_dict[autorizacion]:
                    horarios = HorarioCurso.objects.filter(
                        curso__in=cursos, cupo_disponible_autorizados__gt=0
                    ).order_by('nombre').all()
                else:
                    horario = HorarioCurso.objects.filter(pk=autorizaciones_dict[autorizacion])
                    if horario not in horarios:
                        horarios |= horario
        data = {}
        if horarios and not preinscripcion_mismo_idioma:
            for i in horarios:
                data[str(i.id)] = i.nombre
        else:
            data[str(id)] = RejectedError
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required()
def cargar_descuentos(request):
    error = False
    if request.user.is_authenticated:
        programa_academico_id = request.GET.get('programa_academico')
        oferta_academica = OfertaAcademica.objects.get(programa=programa_academico_id, periodo_id= request.session["periodo_contextualizado_id"])
        descuentos = oferta_academica.descuentos.filter(activo=True)
        data = {}
        for i in descuentos:
            data[str(i.id)] = i.nombre
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required
def preinscripcion_fase_previa(request):
    error = False
    detallado_preinscripcion = {}
    if request.user.is_authenticated:
        responseObject={}
        idioma_id = request.GET['idioma']
        horario_curso = request.GET['horario_curso']
        programa_academico = request.GET['programa_academico']


        try:
            preinscrito = Profile.objects.get(pk = request.user.profile.id)
        except Profile.DoesNotExist:
            preinscrito = None
        try:
            horario = HorarioCurso.objects.get(pk=horario_curso)
        except HorarioCurso.DoesNotExist:
            horario = None
        try:
            periodo = Periodo.objects.get(pk=request.session["periodo_contextualizado_id"])
        except Periodo.DoesNotExist:
            periodo = None
        try:
            idioma = Idioma.objects.get(pk=idioma_id)
        except Idioma.DoesNotExist:
            idioma = None
        try:
            programa = ProgramaAcademico.objects.get(pk=programa_academico)
        except ProgramaAcademico.DoesNotExist:
            programa = None

        if preinscrito and horario and periodo:
            try:
                if request.GET.get('descuento') != '':
                    descuento_id = request.GET.get('descuento')
                else:
                    descuento_id = 0
                descuento = Descuento.objects.get(pk=descuento_id)
                responseObject['descuento_id'] = descuento.id
                responseObject['descuento'] = descuento.nombre
                responseObject['descuento_porcentaje'] = descuento.porcentaje
            except Descuento.DoesNotExist:
                descuento = None
                responseObject['descuento'] = None
                responseObject['descuento_id'] = None
            ayudante = AyudanteFinancieros(preinscrito, periodo)
            tarifa_curso = horario.curso.oferta_academica.tarifa
            valor_inscripcion, detallado_preinscripcion = ayudante.calcular_valor_preinscripcion_curso(tarifa_curso, horario.curso.nivel, descuento, horario.curso.nivel.costo_materiales)

            responseObject['primer_nombre']=request.user.profile.primer_nombre
            responseObject['segundo_nombre'] = request.user.profile.segundo_nombre
            responseObject['primer_apellido'] = request.user.profile.primer_apellido
            responseObject['segundo_apellido'] = request.user.profile.segundo_apellido
            responseObject['tipo_documento'] = request.user.profile.tipo_documento.nombre
            responseObject['numero_documento'] = request.user.profile.numero_documento
            responseObject['periodo'] = periodo.alias
            responseObject['precio'] = str(float(tarifa_curso))
            responseObject['precio_total'] = str(float(valor_inscripcion))
            responseObject['programa_academico'] = programa.nombre

            ##Datos relacionados con la inscripción

            responseObject['idioma'] = idioma_id
            responseObject['horario'] = horario_curso
            responseObject['horario_nombre'] = horario.nombre
            responseObject['idioma_nombre'] = idioma.nombre

            responseObject['detalle'] = detallado_preinscripcion

            strHash = str(responseObject['idioma'])+str(responseObject['horario'])+str(responseObject['periodo'])+str(responseObject['numero_documento'])+"INSCRIPCIONOK"
            responseObject['hash'] = hashlib.sha256(strHash.encode()).hexdigest()

            #Construcción del string de salida
            data = responseObject.copy()
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj, 'detallado' : detallado_preinscripcion})
        else:
            return render(request, 'webservices/error.html', {'resultset': "Error de servidor"})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


class BuscarPreinscripcionesView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'administracion/inscripcion/buscar_preinscripciones.html'


class PreinscripcionesPersonaView(LoginRequiredMixin, generic.ListView):
    model = Preinscripcion
    template_name = 'administracion/inscripcion/preinscripciones_persona.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'
    persona = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = self.persona
        if self.persona:
            context['usuario'] = True
        else:
            context['usuario'] = False
        return context

    def get_queryset(self):
        periodo_id = self.request.session["periodo_contextualizado_id"]
        query = self.request.GET.get('q')
        try:
            persona = Profile.objects.get(numero_documento=query)
        except Profile.DoesNotExist:
            persona = None
        self.persona = persona

        try:
            preinscripcionesCurso = PreinscripcionHorarioCurso.objects.filter(persona=persona,
                                                                              horario_cupo__curso__oferta_academica__periodo__activo=True)
        except PreinscripcionHorarioCurso.DoesNotExist:
            preinscripcionesCurso = []
        try:
            preinscripcionesExamen = PreinscripcionExamen.objects.filter(persona=persona, examen__periodo__activo=True)
        except PreinscripcionExamen.DoesNotExist:
            preinscripcionesExamen = []
        return list(chain(preinscripcionesCurso, preinscripcionesExamen))


@login_required()
@csrf_exempt
def formalizar_vista(request, pk):
    periodo = Periodo.objects.get(pk=request.session["periodo_contextualizado_id"])
    preinscripcionhorariocurso = get_object_or_404(PreinscripcionHorarioCurso, pk=pk)
    recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, preinscripcion=preinscripcionhorariocurso)
    descuento_aplicado = DescuentoAplicado.objects.filter(preinscripcion_generada=preinscripcionhorariocurso, estado_descuento__in=(1,2,4))
    documentos = []
    valor_descuento = None
    validar_descuento = True
    saldo_flag = check_saldo_cargado(recibopreinscripcion)
    reservas_saldos = ReservasSaldo.objects.filter(preinscripcion_reserva=preinscripcionhorariocurso)
    facturacion_form = RequiereFacturacionForm(instance=preinscripcionhorariocurso)

    if descuento_aplicado:
        documentos = DocumentosDescuentoSolicitado.objects.filter(descuento_aplicado=descuento_aplicado[0])
        descuento_aplicado = descuento_aplicado[0]
        valor_descuento = ((recibopreinscripcion.valor_requerido - preinscripcionhorariocurso.horario_cupo.curso.nivel.costo_materiales) * descuento_aplicado.descuento.porcentaje) / 100
    try:
        beca = Beca.objects.get(beneficiario=preinscripcionhorariocurso.persona,
                                periodo_generado__inicio__gte=periodo.inicio - 4,
                                nivel_idioma=preinscripcionhorariocurso.horario_cupo.curso.nivel)
    except Beca.DoesNotExist:
        beca = None

    try:
        matricula = Matricula.objects.get(estudiante=preinscripcionhorariocurso.persona, grupo__horarioCurso__curso=preinscripcionhorariocurso.horario_cupo.curso )
    except Matricula.DoesNotExist:
        matricula = None

    comprobantes_banco = ComprobanteBanco.objects.filter(preinscripcion_generada=preinscripcionhorariocurso)

    calcularPagos = CalcularPagosRecibo(recibopreinscripcion)
    pagado, sobrante, pendiente, pagos = calcularPagos.calcular_pagos()

    tarifa_plena = recibopreinscripcion.valor_requerido - preinscripcionhorariocurso.horario_cupo.curso.nivel.costo_materiales
    if request.method == 'POST':
        facturacion_form = RequiereFacturacionForm(request.POST)
        if facturacion_form.is_valid():
            preinscripcionhorariocurso.requiere_facturacion = facturacion_form.cleaned_data['requiere_facturacion']
            preinscripcionhorariocurso.save()
        if preinscripcionhorariocurso.estado_preinscripcion == 5:
            preinscripcionhorariocurso.estado_preinscripcion = 3
            preinscripcionhorariocurso.save()
        if descuento_aplicado:
            for d in documentos:
                if not d.entregado:
                    validar_descuento = False
            try:
                pago_descuento = Pago.objects.get(financiero=descuento_aplicado)
            except Pago.DoesNotExist:
                pago_descuento = None
            # si todos los documentos de documento estan entregados y no existe un pago para este descuento crear pago
            if validar_descuento and not pago_descuento:
                pago = Pago(realizado_por=preinscripcionhorariocurso.persona,financiero=descuento_aplicado, tipo_preinscripcion=1,recibo_preinscripcion=recibopreinscripcion, aprobo=request.user.profile,fecha_hora=datetime.now(), tipo='Descuento')
                pago.save()
                #actualizar estado de descuento aplicado
                descuento_aplicado.estado_descuento = 2
                descuento_aplicado.save()
        if comprobantes_banco:
            for comprobante in comprobantes_banco:
                try:
                    comprobante_pago = Pago.objects.get(financiero=comprobante)
                except Pago.DoesNotExist:
                    comprobante_pago = None
                if not comprobante_pago:
                    pago_banco = Pago(realizado_por=preinscripcionhorariocurso.persona, financiero=comprobante,
                                tipo_preinscripcion=1, recibo_preinscripcion=recibopreinscripcion,
                                aprobo=request.user.profile, fecha_hora=datetime.now(), tipo='Pago Usuario')
                    pago_banco.save()
                    comprobante.estado_pago = 2
                    comprobante.save()
        pagado, sobrante, pendiente, pagos = calcularPagos.calcular_pagos()
        if pendiente < 0:
            pendiente = 0
        if pendiente == 0 and validar_descuento and preinscripcionhorariocurso.persona.documento_identificacion_entregado and (preinscripcionhorariocurso.estado_preinscripcion == 5 or preinscripcionhorariocurso.estado_preinscripcion == 3):
            preinscripcionhorariocurso.estado_preinscripcion = 1
            preinscripcionhorariocurso.save()
        return HttpResponseRedirect(request.path_info)
    return render(request, "administracion/inscripcion/formalizar_preinscripcion_curso.html",
                  {
                      'preinscripcionhorariocurso': preinscripcionhorariocurso,
                      'recibo': recibopreinscripcion,
                      'descuento_aplicado': descuento_aplicado,
                      'documentos': documentos,
                      'beca': beca,
                      'valor_descuento': valor_descuento,
                      'reservas': reservas_saldos,
                      'matricula': matricula,
                      'pagos': pagos,
                      'pagado': pagado,
                      'sobrante': sobrante,
                      'pendiente': pendiente,
                      'comprobantes_banco': comprobantes_banco,
                      'tarifa_plena': tarifa_plena,
                      'saldo_flag': saldo_flag,
                      'facturacion_form': facturacion_form
                  })

@login_required()
@csrf_exempt
def formalizar_vista_examen(request, pk):
    periodo = Periodo.objects.get(pk=request.session["periodo_contextualizado_id"])
    preinscripcionexamen = get_object_or_404(PreinscripcionExamen, pk=pk)
    recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, preinscripcion=preinscripcionexamen)
    saldo_flag = check_saldo_cargado(recibopreinscripcion)
    reservas_saldos = ReservasSaldo.objects.filter(preinscripcion_reserva=preinscripcionexamen)
    grupo_estudiante = Group.objects.get(name='Estudiante')
    try:
        calificacion = CalificacionExamen.objects.get(preinscripcion_examen=preinscripcionexamen)
    except CalificacionExamen.DoesNotExist:
        calificacion = None
    nivel_asignado = None
    if calificacion:
        if calificacion.nivel:
            nivel_asignado = calificacion.nivel.nombre

    comprobantes_banco = ComprobanteBanco.objects.filter(preinscripcion_generada=preinscripcionexamen)

    calcularPagos = CalcularPagosRecibo(recibopreinscripcion)
    pagado, sobrante, pendiente, pagos = calcularPagos.calcular_pagos()

    tarifa_plena = recibopreinscripcion.valor_requerido
    if request.method == 'POST':
        #Buscar calificacion examen
        try:
            calificacion = CalificacionExamen.objects.get(preinscripcion_examen=preinscripcionexamen)
        except CalificacionExamen.DoesNotExist:
            calificacion = None
        if not calificacion:
            calificacion_examen = CalificacionExamen(preinscripcion_examen=preinscripcionexamen)
            calificacion_examen.save()
        if not usuarioTieneGrupo(preinscripcionexamen.persona.usuario, 'Estudiante'):
            preinscripcionexamen.persona.usuario.groups.add(grupo_estudiante)
        if preinscripcionexamen.estado_preinscripcion == 5:
            preinscripcionexamen.estado_preinscripcion = 3
            preinscripcionexamen.save()
        if comprobantes_banco:
            for comprobante in comprobantes_banco:
                try:
                    comprobante_pago = Pago.objects.get(financiero=comprobante)
                except Pago.DoesNotExist:
                    comprobante_pago = None
                if not comprobante_pago:
                    pago_banco = Pago(realizado_por=preinscripcionexamen.persona, financiero=comprobante,
                                tipo_preinscripcion=2, recibo_preinscripcion=recibopreinscripcion,
                                aprobo=request.user.profile, fecha_hora=datetime.now(), tipo='Pago Usuario')
                    pago_banco.save()
                    comprobante.estado_pago = 2
                    comprobante.save()
        calcularPagos = CalcularPagosRecibo(recibopreinscripcion)
        pagado, sobrante, pendiente, pagos = calcularPagos.calcular_pagos()
        if pendiente < 0:
            pendiente = 0
        if pendiente == 0 and preinscripcionexamen.persona.documento_identificacion_entregado and (preinscripcionexamen.estado_preinscripcion == 5 or preinscripcionexamen.estado_preinscripcion == 3):
            preinscripcionexamen.estado_preinscripcion = 1
            preinscripcionexamen.save()
        return HttpResponseRedirect(request.path_info)
    return render(request, "administracion/inscripcion/formalizar_preinscripcion_examen.html", {'preinscripcionexamen' : preinscripcionexamen, 'reservas' : reservas_saldos,\
        'recibo' : recibopreinscripcion, 'nivel_asignado' : nivel_asignado, 'pagos' : pagos, 'pagado': pagado, 'sobrante' : sobrante, \
        'pendiente' : pendiente, 'comprobantes_banco' : comprobantes_banco, 'tarifa_plena' : tarifa_plena, 'saldo_flag' : saldo_flag})


def preinscribir_persona(persona, descuento, horario_curso, periodo):
    hoy = timezone.now()
    error = None
    preinscripcion = {}
    if persona and horario_curso and periodo:
        ofertas_periodo = OfertaAcademica.objects.filter(periodo=periodo)

        niveles = Nivel.objects.filter(idioma_id=horario_curso.curso.nivel.idioma.id)
        preinscripcion_previa = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion__in=[1, 3, 5],
                                                                          horario_cupo=horario_curso,
                                                                          persona=persona, horario_cupo__curso__oferta_academica__in=ofertas_periodo)  # Estado 6: Cancelado
        preinscripcion_mismo_idioma = PreinscripcionHorarioCurso.objects.filter(estado_preinscripcion__in=[1, 3, 5],
                                                                                horario_cupo__curso__nivel__in=niveles,
                                                                                persona=persona, horario_cupo__curso__oferta_academica__in=ofertas_periodo)
        preinscripcion_horario_existente = PreinscripcionHorarioCurso.objects.filter(
            estado_preinscripcion__in=[1, 3, 5],
            horario_cupo__horario=horario_curso.horario,
            persona=persona, horario_cupo__curso__oferta_academica__in=ofertas_periodo)
        if not preinscripcion_previa and not preinscripcion_mismo_idioma and not preinscripcion_horario_existente:
            strHash = str(horario_curso.curso.nivel.idioma.id) + str(horario_curso.id) + str(periodo.id) + str(persona.numero_documento) + "INSCRIPCIONOK"
            hash_code = hashlib.sha256(strHash.encode()).hexdigest()
            ayudante = AyudanteFinancieros(persona, periodo)
            tarifa_curso = horario_curso.curso.oferta_academica.tarifa
            valor_inscripcion, detallado_preinscripcion = ayudante.calcular_valor_preinscripcion_curso(tarifa_curso,
                                                                                                       horario_curso.curso.nivel,
                                                                                                       descuento,
                                                                                                       horario_curso.curso.nivel.costo_materiales)
            # buscar si es autorizado
            autorizado_curso = AutorizadoCurso.objects.filter(numero_documento=persona.numero_documento,
                                                              periodo=periodo, curso_autorizado=horario_curso.curso,
                                                              estado__in=[1, 3]).all().first()
            if autorizado_curso and horario_curso.cupo_disponible_autorizados > 0:
                preinscripcion_curso = PreinscripcionHorarioCurso(persona=persona,
                                                                  valor_preinscripcion=valor_inscripcion,
                                                                  codigo_hash=hash_code, horario_cupo=horario_curso,
                                                                  descuento_solicitado=descuento)
                preinscripcion_curso.save()
                recibo = ReciboPreinscripcion.objects.create(preinscrito=persona,
                                                             preinscripcion=preinscripcion_curso,
                                                             valor_requerido=tarifa_curso + horario_curso.curso.nivel.costo_materiales,
                                                             estado_recibo=2)
                logger.info("Recibo preinscripción creado satisfactoriamente")
                horario_curso.cupo_disponible_autorizados = horario_curso.cupo_disponible_autorizados - 1
                autorizado_curso.estado = 2  # completa
                autorizado_curso.save()
                horario_curso.save()
                if descuento:
                    documentos_requeridos = preinscripcion_curso.descuento_solicitado.documentos_requeridos.all()
                else:
                    documentos_requeridos = []
                # actualizar Financieros utilizados
                ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                logger.info("Financieros actualizados")

                preinscripcion = {'preinscripcion_curso': preinscripcion_curso, 'documentos_requeridos': documentos_requeridos, 'detallado': detallado_preinscripcion}

                return error, preinscripcion
            elif horario_curso.cupo_disponible > 0:
                preinscripcion_curso = PreinscripcionHorarioCurso(persona=persona,
                                                                  valor_preinscripcion=valor_inscripcion,
                                                                  codigo_hash=hash_code, horario_cupo=horario_curso,
                                                                  descuento_solicitado=descuento)
                preinscripcion_curso.save()
                recibo = ReciboPreinscripcion.objects.create(preinscrito=persona,
                                                             preinscripcion=preinscripcion_curso,
                                                             valor_requerido=tarifa_curso + horario_curso.curso.nivel.costo_materiales,
                                                             estado_recibo=2)
                logger.info("Recibo preinscripción creado satisfactoriamente")
                horario_curso.cupo_disponible = horario_curso.cupo_disponible - 1
                horario_curso.save()
                if descuento:
                    documentos_requeridos = preinscripcion_curso.descuento_solicitado.documentos_requeridos.all()
                else:
                    documentos_requeridos = []
                # actualizar Financieros utilizados
                ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                logger.info("Financieros actualizados")

                html_message = loader.render_to_string(
                    'administracion/inscripcion/preinscripcion_curso_confirmacion_email.html',
                    {'preinscripcion_curso': preinscripcion_curso, 'documentos_requeridos': documentos_requeridos,
                     'detallado': detallado_preinscripcion})
                send_mail('Confirmación Preinscripción Curso', '', 'sialex_fchbog@unal.edu.co',
                          ['sialex_fchbog@unal.edu.co'], fail_silently=True, html_message=html_message)
                preinscripcion = {'preinscripcion_curso': preinscripcion_curso,
                               'documentos_requeridos': documentos_requeridos, 'detallado': detallado_preinscripcion}
                return error, preinscripcion
            else:
                error = 'la asignación de cupos ha finalizado'
        else:
            if preinscripcion_previa:
                error = 'Ya existe una preinscripción para este usuario, curso y horario en el presente periodo'
            if preinscripcion_mismo_idioma:
                error = 'Ya existe una preinscripción para este idioma en el presente periodo'
            if preinscripcion_horario_existente:
                error = 'Ya cuenta con una preinscripción en esta franja horaria en el presente periodo'
        return error, preinscripcion

@login_required
def preinscripcion_curso_lote(request):

    periodo_id = request.session['periodo_contextualizado_id']
    try:
        periodo = Periodo.objects.get(pk=periodo_id)
    except Periodo.DoesNotExist:
        periodo = None

    campos = 'Tipo_documento_identidad,Numero_documento,Descuento_solicitado'
    tipos_documento = TipoDocumentoIdentidad.objects.values_list('nombre', flat=True)
    descuentos = Descuento.objects.all().order_by('id')
    ERROR = 'ERROR'
    EXITO = 'EXITO'


    if request.method == 'GET':
        form = PreinscripcionCursoLoteForm()
    else:
        form = PreinscripcionCursoLoteForm(request.POST, request.FILES)
        if form.is_valid():
            curso_id = request.POST['curso']
            horario_curso_id = request.POST['horario_curso']
            file_data = None
            try:
                curso = Curso.objects.get(pk = curso_id)
            except Curso.DoesNotExist:
                curso = None

            try:
                horario_curso = HorarioCurso.objects.get(pk= horario_curso_id)
            except HorarioCurso.DoesNotExist:
                horario_curso = None

            try:
                archivo = request.FILES['archivo']
                if not archivo.name.endswith('.csv'):
                    messages.warning(request, 'El archivo debe tener la extensión .csv')
                    return render(request,
                                  'administracion/preinscripciones/preinscripcion_opciones.html')
                else:
                    file_data = archivo.read().decode("utf-8")

            except Exception as e:
                messages.warning(request, "Ocurrio un error al leer el archivo " + repr(e))

            i = 1
            data_dict = {}
            data_dict[0] = ['tipo_documento', 'documento', 'descuento_solicitado', 'curso', 'horario', 'resultado']
            preinscritos = 0
            documentos = []

            if file_data:
                lines = file_data.split('\n')
                for line in lines:
                    if line != '' and len(line.split(',')) > 1:
                        fields = line.split(',')
                        tipo_doc = fields[0].strip().upper()
                        message = EXITO + ' :Preinscripcion_exitosa'
                        if tipo_doc not in tipos_documento:
                            message = ERROR + ' :El_tipo_documento_' + fields[0] + ' _no_es_valido'
                        else:
                            tipo_documento = TipoDocumentoIdentidad.objects.get(nombre=tipo_doc).id
                            numero_documento = fields[1].strip()
                            if numero_documento != '':
                                try:
                                    persona = Profile.objects.get(numero_documento=numero_documento, tipo_documento=tipo_documento)
                                except Profile.DoesNotExist:
                                    persona = None

                                if not persona:
                                    message = ERROR + ': La_persona_con_documento ' + numero_documento + '_no_esta_registrada'
                                elif persona and horario_curso:
                                    if numero_documento not in documentos:

                                        preinscripcion_existente = PreinscripcionHorarioCurso.objects.filter(persona=persona, horario_cupo_id=horario_curso_id, estado_preinscripcion__in=[1,3,5])
                                        if preinscripcion_existente:
                                            message = ERROR + ' : La_persona_con_documento ' + numero_documento + '_ya_esta_preinscrito_al_curso ' + horario_curso.nombre
                                        else:
                                            descuento_id = fields[2].strip()
                                            if descuento_id != '':
                                                try:
                                                    descuento = Descuento.objects.get(pk=descuento_id)
                                                except Descuento.DoesNotExist:
                                                    descuento = None
                                            else:
                                                descuento = None
                                            error, preinscripcion = preinscribir_persona(persona, descuento, horario_curso, periodo)
                                            if preinscripcion and not error:
                                                documentos.append(numero_documento)
                                                preinscritos += 1
                                            elif error:
                                                message = 'ERROR: ' + error
                                    else:
                                        message = 'ERROR: ' + 'Documento_' + numero_documento + '_repetido_en_el_archivo'
                            else:
                                message = 'ERROR: ' + 'Campo_documento_vacio '

                        data_dict[i] = [fields[0], fields[1], fields[2], curso.nombre, horario_curso.nombre, message]
                    else:
                        message = ERROR + ': La_linea' + str(i) + '_no_tiene_el_formato_requerido'
                        data_dict[i] = [line, '', '', '', message]

                    i += 1

                #TODO: PREINSCRIBIR
            messages.add_message(request, messages.SUCCESS, 'Se han preinscrito a '
                                 + str(preinscritos) + ' personas al curso: ' + curso.nombre)
            return render(request,
                          'administracion/cargaEnLote/resultado_lote.html',
                          {'resultado': data_dict, 'tipo': 'preinscripcion_curso'})

    context = {'form': form, 'periodo': periodo,'campos': campos, 'tipos_documento': tipos_documento, 'descuentos': descuentos}
    return render(request, 'administracion/inscripcion/lote/preinscripcion_curso_lote.html', context)

@login_required()
def cargarSaldoFavor(request, pk):
    periodo_id = request.session['periodo_contextualizado_id']
    recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, pk=pk)
    calcularPagos = CalcularPagosRecibo(recibopreinscripcion)
    pagado, sobrante, pendiente, pagos = calcularPagos.calcular_pagos()
    if request.method == 'POST':
        if not check_saldo_cargado(recibopreinscripcion):
            saldo = SaldoAFavor(beneficiario=recibopreinscripcion.preinscripcion.persona, periodo_generado_id=periodo_id, valor=sobrante, activo=True, recibo_preinscripcion_generado=recibopreinscripcion)
            saldo.save()
            return redirect('formalizar-curso', pk=recibopreinscripcion.preinscripcion.id)
        else:
            messages.add_message(request, messages.WARNING,'Ya se cargo un saldo para esta preinscripcion previamente')
            return redirect('formalizar-curso', pk=recibopreinscripcion.preinscripcion.id)
    return render(request, 'administracion/inscripcion/cargar_saldo_a_favor.html', {'sobrante' : sobrante })

@login_required()
def aplicarSaldoPago(request,pk):
    periodo_id = request.session['periodo_contextualizado_id']
    reserva = get_object_or_404(ReservasSaldo, pk=pk)
    try:
        recibopreinscripcion = ReciboPreinscripcion.objects.get(preinscripcion=reserva.preinscripcion_reserva)
    except ReciboPreinscripcion.DoesNotExist:
        recibopreinscripcion = None
    preinscripcion_curso = PreinscripcionHorarioCurso.objects.filter(recibopreinscripcion=recibopreinscripcion)
    if preinscripcion_curso:
        tipo_preinscripcion = 1
    else:
        tipo_preinscripcion = 2
    if request.method == 'POST':
        reserva.pagado = True
        reserva.save()
        valor_saldo_actual = reserva.saldo.valor
        nuevo_valor_saldo = valor_saldo_actual - reserva.valor
        saldo = get_object_or_404(SaldoAFavor, pk=reserva.saldo.id)
        saldo.valor = reserva.valor
        saldo.activo = False
        saldo.save()
        if nuevo_valor_saldo > 0:
            nuevo_saldo = SaldoAFavor(beneficiario=reserva.preinscripcion_reserva.persona, periodo_generado_id=periodo_id, valor=float(nuevo_valor_saldo), activo=True, recibo_preinscripcion_generado=reserva.preinscripcion_reserva.recibopreinscripcion)
            nuevo_saldo.save()
        pago = Pago(realizado_por= reserva.preinscripcion_reserva.persona, financiero=reserva.saldo,
                    tipo_preinscripcion=tipo_preinscripcion, recibo_preinscripcion=recibopreinscripcion, aprobo=request.user.profile,
                    fecha_hora=datetime.now(), tipo='Saldo a favor')
        pago.save()
        return redirect('formalizar-curso', pk=reserva.preinscripcion_reserva.id)
    return render(request, 'administracion/inscripcion/confirmar_saldo_pago.html', {'reserva': reserva})

@login_required()
def aplicarBecaPago(request,pk):
    periodo_id = request.session['periodo_contextualizado_id']
    try:
        preinscripcion = PreinscripcionHorarioCurso.objects.get(pk=pk)
    except PreinscripcionHorarioCurso.DoesNotExist:
        preinscripcion = None
    try:
        recibopreinscripcion = ReciboPreinscripcion.objects.get(preinscripcion_id=pk)
    except ReciboPreinscripcion.DoesNotExist:
        recibopreinscripcion = None
    preinscripcion_curso = PreinscripcionHorarioCurso.objects.filter(recibopreinscripcion=recibopreinscripcion)
    if preinscripcion_curso:
        tipo_preinscripcion = 1
    else:
        tipo_preinscripcion = 2
    if preinscripcion:
        try:
            beca = Beca.objects.get(estado_beca=2, beneficiario=preinscripcion.persona,
                                nivel_idioma=preinscripcion.horario_cupo.curso.nivel)
        except Beca.DoesNotExist:
            beca = None
    if request.method == 'POST' and beca:
            beca.estado_beca = 3
            beca.save()
            pago = Pago(realizado_por= request.user.profile, financiero=beca,
                    tipo_preinscripcion=tipo_preinscripcion, recibo_preinscripcion=recibopreinscripcion, aprobo=request.user.profile,
                    fecha_hora=datetime.now(), tipo='Beca')
            pago.save()
            return redirect('formalizar-curso', pk=preinscripcion.id)
    return render(request, 'administracion/inscripcion/confirmar_beca_pago.html', {'beca': beca})
