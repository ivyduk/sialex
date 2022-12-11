import operator
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction, IntegrityError
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy

from administracion.views.busqueda_list import BusquedaGenerica
from ..forms import PersonaContactoForm, BasePersonaContactoFormSet, EditProfileForm, \
    ExamenClasificacionForm, PersonaAdministracionForm
from ..models import Profile, PersonaContacto, Preinscripcion, PreinscripcionExamen, PreinscripcionHorarioCurso
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404


class PersonaDetailView(LoginRequiredMixin,DetailView):

    model = Profile
    template_name = 'administracion/persona/persona_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personas_contacto'] = PersonaContacto.objects.filter(profile__id=self.kwargs['pk']).all()
        return context

@login_required
def personas_list(request):

    campos = ['usuario__email',
              'tipo_documento__nombre',
              'numero_documento',
              'ciudad_expedicion_documento__nombre',
              'primer_nombre',
              'segundo_nombre',
              'primer_apellido',
              'segundo_apellido',
              'ciudad_nacimiento__nombre',
              'ciudad_residencia__nombre',
              'direccion_residencia',
              'telefono_fijo',
              'telefono_celular',
              'tipo_sangre',
              'eps__nombre',
              'profile_completed',
              ]

    busqueda_generica = BusquedaGenerica()
    object_list = Profile.objects.all()
    query_string = request.GET.get('q')

    if query_string:
        consulta = busqueda_generica.get_query(query_string, campos)
        object_list = Profile.objects.filter(consulta).order_by('numero_documento')
    page = request.GET.get('page')
    paginator = Paginator(object_list, 20)
    try:
        personas = paginator.page(page)
    except PageNotAnInteger:
        personas = paginator.page(1)
    except EmptyPage:
        personas = paginator.page(paginator.num_pages)

    return render(request, 'administracion/persona/persona_list.html', {'object_list': personas, 'total': len(object_list)})


class EditarPersona(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = PersonaAdministracionForm
    template_name = 'administracion/persona/persona_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.object

        PersonaContactoFormSet = formset_factory(PersonaContactoForm, formset=BasePersonaContactoFormSet,
                                                 can_delete=True,
                                                 extra=0, max_num=3, min_num=1, validate_max=True, validate_min=True)
        personas_contacto = PersonaContacto.objects.filter(profile=instance).all()
        contactos = PersonaContacto.objects.filter(profile=instance).order_by('nombres')
        datos_contactos = [{'nombres': c.nombres, 'apellidos': c.apellidos, 'numero_celular': c.numero_celular,
                            'correo_electronico': c.correo_electronico, 'parentesco': c.parentesco}
                           for c in contactos]

        persona_contacto_formset = PersonaContactoFormSet(initial=datos_contactos)

        indicativo_fijo = instance.indicativo_fijo
        indicativo_celular = instance.indicativo_celular

        context['indicativo_fijo'] = indicativo_fijo
        context['indicativo_celular'] = indicativo_celular
        context['persona_contacto_formset'] = persona_contacto_formset
        context['personas_contacto'] = personas_contacto
        return context

    def form_valid(self, form):
        instance = self.object
        tel_fijo = str(form.instance.telefono_fijo).split('+')
        tel_celular = str(form.instance.telefono_celular).split('+')
        PersonaContactoFormSet = formset_factory(PersonaContactoForm, formset=BasePersonaContactoFormSet,
                                                 can_delete=True,
                                                 extra=0, max_num=3, min_num=1, validate_max=True, validate_min=True)
        persona_contacto_formset = PersonaContactoFormSet(self.request.POST)

        instance.indicativo_fijo = tel_fijo[0].upper()
        instance.telefono_fijo = tel_fijo[1]
        instance.indicativo_celular = tel_celular[0].upper()
        instance.telefono_celular = tel_celular[1]
        instance.save()

        nuevos_contactos = []

        if persona_contacto_formset.is_valid():
            for contacto_form in persona_contacto_formset:

                nombres = contacto_form.cleaned_data['nombres']
                apellidos = contacto_form.cleaned_data.get('apellidos')
                numero_celular = contacto_form.cleaned_data.get('numero_celular')
                correo_electronico = contacto_form.cleaned_data.get('correo_electronico')
                parentesco = contacto_form.cleaned_data.get('parentesco')

                if nombres and apellidos and numero_celular and correo_electronico and parentesco:
                    nuevos_contactos.append(PersonaContacto(nombres=nombres, apellidos=apellidos,
                                                        numero_celular=numero_celular,
                                                        correo_electronico=correo_electronico, profile=instance,
                                                        parentesco=parentesco))

            try:
                with transaction.atomic():
                    PersonaContacto.objects.filter(profile=instance).delete()
                    PersonaContacto.objects.bulk_create(nuevos_contactos)

                    # Notificacion de exito
                    messages.success(self.request, 'Se han guardado los cambios sobre los datos personales de ' +
                                  ' ' + instance.getNombres() + ' ' + instance.getApellidos())

            except IntegrityError:
                messages.error(self.request, 'Hubo un error al guardar sus datos personales')

        form.save()

        return HttpResponseRedirect(self.get_success_url())


class EditarPersonaDocumentoEntregado(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'administracion/persona/persona_documento_entregado_form.html'
    fields = ["documento_identificacion_entregado"]
    success_message = 'Actualizados documentos de identificación.'

    def post(self, request, **kwargs):
        self.object = self.get_object()
        if not request.POST.get('documento_identificacion_entregado'):
            preinscripcion_id = self.kwargs["preinscripcion"]
            precurso = Preinscripcion.objects.filter(id=preinscripcion_id).first()

            if precurso.estado_preinscripcion == 1:
                precurso.estado_preinscripcion = 3
                precurso.save()

        return super(EditarPersonaDocumentoEntregado, self).post(request, **kwargs)

    def get_success_url(self, *args, **kwargs):
        preinscripcion_id = self.kwargs["preinscripcion"]
        preinscripcion = PreinscripcionExamen.objects.filter(id=preinscripcion_id).first()
        if not preinscripcion:
            return reverse_lazy('formalizar-curso',
                                kwargs={'pk': preinscripcion_id})
        else:
            return reverse_lazy('formalizar-examen',
                                kwargs={'pk': preinscripcion_id})

