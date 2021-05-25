from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, Form
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from administracion.models import Autorizado, Idioma, TipoDocumentoIdentidad, AutorizadoCurso, AutorizadoExamen, \
    ExamenClasificacion, Periodo, Profile
from django.utils import timezone
from django.contrib import messages

class AutorizadoForm(ModelForm):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all().order_by('nombre'))

    class Meta:
        model = AutorizadoCurso
        exclude = ['periodo', 'autorizado_por', 'estado', 'curso_autorizado', 'horario_curso_autorizado', 'fecha_hora_autorizacion']

    def clean(self):
        cleaned_data = super(AutorizadoForm,self).clean()

class AutorizadoLoteForm(Form):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all().order_by('nombre'))
    archivo = forms.FileField(required=True)
    motivo = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))

    def clean(self):
        cleaned_data = super(AutorizadoLoteForm,self).clean()


class AutorizadoExamenForm(ModelForm):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all().order_by('nombre'))

    class Meta:
        model = AutorizadoExamen
        exclude = ['periodo', 'autorizado_por', 'estado', 'curso', 'horario_curso', 'fecha_hora_autorizacion']

    def clean(self):
        cleaned_data = super(AutorizadoExamenForm,self).clean()

class AutorizadoExamenLoteForm(Form):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all())
    archivo = forms.FileField(required=True)
    motivo = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))

    def clean(self):
        cleaned_data = super(AutorizadoExamenLoteForm,self).clean()

def autorizadoExamenUpdate(request, pk):

    template_name = 'administracion/autorizado/autorizadoExamen/autorizado_examen_form.html'
    instance = AutorizadoExamen.objects.get(pk = pk)
    periodo_id = instance.periodo.id
    hoy = timezone.now()
    examen_inicial = instance.examen

    if request.method == "GET":

        if instance.estado == 2:
            messages.add_message(request, messages.WARNING, 'La persona que escogió NO puede ser modificada porque ya usó el cupo')
            return redirect('autorizado_opciones')

        periodo = Periodo.objects.get(pk=periodo_id)

        tipo_documento = instance.tipo_documento
        numero_documento = instance.numero_documento
        motivo = instance.motivo
        idioma = examen_inicial.idioma

        examenes = ExamenClasificacion.objects.filter(idioma = idioma.id, periodo_id=periodo_id).exclude(pk = examen_inicial.id).order_by('nombre').all()

        initial = {'tipo_documento': tipo_documento, 'numero_documento': numero_documento,
                  'motivo': motivo,'idioma': idioma.id}

        form = AutorizadoExamenForm(initial=initial)
        return render(request, template_name, {'form':form, 'periodo': periodo,
                                               'examen_inicial': examen_inicial,
                                               'examenes': examenes})
    else:
        form = AutorizadoExamenForm(request.POST)

        if form.is_valid():
            examen_id = request.POST['examen']
            autoriza = Profile.objects.get(pk=request.user.profile.id)
            numero_documento = request.POST['numero_documento']
            tipo_documento = request.POST['tipo_documento']
            motivo = request.POST['motivo']

            instance.tipo_documento = TipoDocumentoIdentidad.objects.get(pk=tipo_documento)
            instance.numero_documento = numero_documento
            instance.periodo_id = periodo_id
            instance.motivo = motivo
            instance.examen_id = examen_id

            instance.autorizado_por = autoriza
            instance.fecha_hora_autorizacion = hoy
            instance.save()

            messages.add_message(request, messages.SUCCESS,'Se ha modificado la persona autorizada')

            return redirect('autorizado_opciones')


