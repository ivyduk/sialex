import hashlib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy

from administracion.forms.inscripcionForm import PreinscripcionExamenForm
from administracion.modules import AyudanteFinancieros
from administracion.util import get_barcode_image
from ..models import Profile, ExamenClasificacion, \
    PreinscripcionExamen, Periodo, Idioma, ReciboPreinscripcion, \
    AutorizadoExamen, PreinscripcionHorarioCurso, OfertaAcademica
from django.utils import timezone

from django.contrib import messages
import json
from datetime import datetime
from django.db import transaction, IntegrityError
import logging
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView, DeleteView

from django.template import loader
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class PreinscripcionExamenListView(LoginRequiredMixin, ListView):
    model = PreinscripcionExamen
    template_name = 'administracion/inscripcion/mis_inscripciones.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        perfil = Profile.objects.get(usuario=self.request.user)
        periodo_id = self.request.session["periodo_contextualizado_id"]
        return PreinscripcionExamen.objects.filter(persona=perfil, examen__periodo_id=periodo_id)

class PreinscripcionExamenDetailView(LoginRequiredMixin,DetailView):
    model = PreinscripcionExamen
    template_name = 'administracion/inscripcion/examenClasificacion/preinscripcion_examen_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class PreinscripcionExamenDelete(LoginRequiredMixin, DeleteView):

    model = PreinscripcionExamen
    template_name = 'administracion/inscripcion/examenClasificacion/preinscripcion_examen_confirm_delete.html'
    success_url = reverse_lazy('mis-inscripciones')



@login_required
def preinscripcionExamenView(request):

    mensaje_examenes_disponibles = ''
    hoy = timezone.now()
    if request.method == 'GET':
        form = PreinscripcionExamenForm()
        #examenes_disponibles = buscar_examenes_disponibles(request, None)
        #if len(examenes_disponibles) == 0:
        #    mensaje_examenes_disponibles = 'En este momento no hay exámenes de clasificación disponibles en proceso de preinscripción'
    else:
        form = PreinscripcionExamenForm(request.POST)
        idioma_id = request.POST['idioma']
        examen_id = request.POST['examen']
        periodo_id = request.session["periodo_contextualizado_id"]
        hash_code = request.POST["hash"]
        if form.is_valid():

            try:
                preinscrito = Profile.objects.get(pk = request.user.profile.id)
            except Profile.DoesNotExist:
                preinscrito = None
            try:
                periodo = Periodo.objects.get(pk=periodo_id)
            except Periodo.DoesNotExist:
                periodo = None

            if examen_id != None and examen_id != '':

                try:
                    examen = ExamenClasificacion.objects.get(pk=examen_id)
                except ExamenClasificacion.DoesNotExist:
                    examen = None

                if examen and periodo and preinscrito:

                    ofertas_academicas = OfertaAcademica.objects.filter(programa__idioma_id=idioma_id)
                    examenes_encontrados = PreinscripcionExamen.objects.filter(
                        examen=examen,
                        persona=preinscrito,
                        estado_preinscripcion__in=[1, 3, 4, 5],
                        examen__periodo_id=periodo.id,
                    ).all() #Estado: Inscrito, Pendiente, Aplazado, Preinscrito
                    preinscripcion_curso = PreinscripcionHorarioCurso.objects.filter(
                        horario_cupo__curso__oferta_academica__in=ofertas_academicas,
                        persona=preinscrito, estado_preinscripcion__in=[1, 3, 5],
                        horario_cupo__curso__oferta_academica__periodo__lte=periodo.inicio - 4
                    ).first()
                    if preinscripcion_curso or len(examenes_encontrados) > 0:
                        if preinscripcion_curso:
                            form.add_error(
                                'idioma', 'Ya existe una preinscripción a un curso al mismo idioma'
                                          ' en el periodo: {}'.format(
                                    preinscripcion_curso.horario_cupo.curso.oferta_academica.periodo.alias
                                )
                            )
                        elif len(examenes_encontrados) > 0:
                            form.add_error('idioma',
                                       'Ya existe una preinscripción a este examen de este usuario en el presente periodo')
                    else:
                        tarifa_examen = examen.tarifa

                        ayudante = AyudanteFinancieros(preinscrito, periodo)
                        valor_inscripcion, detallado_preinscripcion = ayudante.calcular_valor_preinscripcion_examen(tarifa_examen)
                        autorizado_examen = AutorizadoExamen.objects.filter(numero_documento=preinscrito.numero_documento,
                                                                            periodo=periodo, examen=examen, estado__in=[1,3]).all().first()
                        if autorizado_examen and examen.cupo_disponible_autorizado > 0:
                            preinscripcion_examen = PreinscripcionExamen(persona = preinscrito, examen = examen, fecha_preinscripcion=hoy, valor_preinscripcion=valor_inscripcion, codigo_hash=hash_code)
                            preinscripcion_examen.save()

                            recibo = ReciboPreinscripcion.objects.create(preinscrito=preinscrito,
                                                                     preinscripcion=preinscripcion_examen,
                                                                     valor_requerido=valor_inscripcion, estado_recibo=2)
                            logger.info("Recibo preinscripción a examen creado satisfactoriamente")

                            examen.cupo_disponible_autorizado -= 1
                            autorizado_examen.estado = 2 #completa
                            autorizado_examen.save()
                            examen.save()

                            ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                            logger.info("Financieros actualizados")

                            html_message = loader.render_to_string('administracion/inscripcion/preinscripcion_examen_email.html', {'preinscripcion_examen': preinscripcion_examen,
                                    'detallado' : detallado_preinscripcion}, request=request)
                            send_mail('Confirmación Preinscripción Examen','','sialex_fchbog@unal.edu.co',[preinscrito.usuario.email],fail_silently=True,html_message=html_message)

                            return render(request, 'administracion/inscripcion/preinscripcion_examen_confirmacion.html',
                                    {'preinscripcion_examen': preinscripcion_examen,
                                    'detallado' : detallado_preinscripcion})
                        elif examen.cupo_disponible > 0:  # preinscripcion regular
                            preinscripcion_examen = PreinscripcionExamen(persona = preinscrito, examen = examen, fecha_preinscripcion=hoy, valor_preinscripcion=valor_inscripcion, codigo_hash=hash_code)
                            preinscripcion_examen.save()

                            recibo = ReciboPreinscripcion.objects.create(preinscrito=preinscrito,
                                                                     preinscripcion=preinscripcion_examen,
                                                                     valor_requerido=valor_inscripcion, estado_recibo=2)
                            logger.info("Recibo preinscripción a examen creado satisfactoriamente")
                            examen.cupo_disponible -= 1
                            examen.save()

                            ayudante.actualizar_financieros_creacion_recibo(recibo, detallado_preinscripcion)
                            logger.info("Financieros actualizados")

                            html_message = loader.render_to_string(
                                'administracion/inscripcion/preinscripcion_examen_email.html',
                                {'preinscripcion_examen': preinscripcion_examen,
                                 'detallado' : detallado_preinscripcion}, request=request
                            )
                            send_mail(
                                'Confirmación Preinscripción Examen',
                                '',
                                'sialex_fchbog@unal.edu.co',
                                [preinscrito.usuario.email],
                                fail_silently=True,
                                html_message=html_message
                            )

                            return render(request, 'administracion/inscripcion/preinscripcion_examen_confirmacion.html',
                                    {'preinscripcion_examen': preinscripcion_examen,
                                    'detallado' : detallado_preinscripcion})
                        else:
                            form.add_error('idioma', '¡Lo sentimos, la asignación de cupos ha finalizado!')
    return render(request, 'administracion/inscripcion/examenClasificacion/preinscripcion_examen.html', {'form': form, 'mensaje_examenes': mensaje_examenes_disponibles})

def calcularEdad(fechaNacimiento):

    fechaNacimiento = datetime.strptime(str(fechaNacimiento), "%Y-%m-%d")
    now = datetime.now()
    diferencia = now - fechaNacimiento

    return int((diferencia.days + diferencia.seconds/86400.0) / 365.2425)

@login_required
def preinscripcion_examen_fase_previa(request):
    error = False
    if request.user.is_authenticated:
        responseObject = {}
        idioma_id = request.GET['idioma']
        examen_id = request.GET['examen']
        periodo_id = request.session["periodo_contextualizado_id"]

        try:
            idioma = Idioma.objects.get(pk=idioma_id)
        except Idioma.DoesNotExist:
            idioma = None

        try:
            preinscrito = Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            preinscrito = None
        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            periodo = None
        try:
            examen = ExamenClasificacion.objects.get(pk=examen_id)
        except ExamenClasificacion.DoesNotExist:
            examen = None
        if preinscrito and periodo and examen:
            ayudante = AyudanteFinancieros(preinscrito, periodo)
            tarifa_examen = examen.tarifa
            valor_inscripcion, detallado_preinscripcion = ayudante.calcular_valor_preinscripcion_examen(tarifa_examen)
            #Datos personales
            responseObject['primer_nombre'] = request.user.profile.primer_nombre
            responseObject['segundo_nombre'] = request.user.profile.segundo_nombre
            responseObject['primer_apellido'] = request.user.profile.primer_apellido
            responseObject['segundo_apellido'] = request.user.profile.segundo_apellido
            responseObject['tipo_documento'] = request.user.profile.tipo_documento.nombre
            responseObject['numero_documento'] = request.user.profile.numero_documento

            #Datos de la preinscripcion
            responseObject['periodo'] = periodo.alias
            responseObject['idioma'] = idioma_id
            responseObject['examen'] = examen_id
            responseObject['idioma_nombre'] = idioma.nombre
            responseObject['examen_nombre'] = examen.nombre
            responseObject['precio'] = str(float(tarifa_examen))
            responseObject['precio_total'] = str(float(valor_inscripcion))


            responseObject['detalle'] = detallado_preinscripcion
            strHash = str(responseObject['numero_documento'] + responseObject['idioma']) + str(responseObject['examen']) + "INSCRIPCIONOK"
            responseObject['hash'] = hashlib.sha256(strHash.encode()).hexdigest()


            # Construcción del string de salida
            data = responseObject.copy()
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html',
                      {'resultset': serialized_obj, 'detallado': detallado_preinscripcion})

    else:
        return render(request, 'webservices/error.html', {'resultset': "Error de servidor"})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

