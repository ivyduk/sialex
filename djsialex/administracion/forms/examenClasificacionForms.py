from django import forms
from django.forms.formsets import BaseFormSet

from administracion.models import ExamenClasificacion, CalificacionExamen, Idioma, Nivel, Docente
from bootstrap_datepicker_plus import DateTimePickerInput
from datetime import datetime
import pytz
from django.db.models import Q

class ExamenClasificacionForm(forms.ModelForm):


    class Meta:
        model = ExamenClasificacion
        fields = ('periodo',
                  'idioma',
                  'nombre',
                  'cupo_inicial',
                  'cupo_autorizado',
                  'tarifa',
                  'edad_minima',
                  'lugar_aplicacion',
                  'fecha_hora',
                  'fecha_hora_recepcion_documentos',
                  'docentes_evaluadores')

        labels = {
            'edad_minima': 'Edad mínima',
            'cupo_inicial': 'Cupos regulares',
            'cupo_autorizado': 'Cupos autorizados',
            'lugar_aplicacion': 'Lugar aplicación',
            'fecha_hora': 'Fecha y hora examen',
            'fecha_hora_recepcion_documentos': 'Información acerca del examen y de la recepción de documentos'
        }

        FORMAT = '%Y-%m-%d %H:%M'

        widgets = {'fecha_hora': DateTimePickerInput(format=FORMAT),
                   }

    def __init__(self, *args, **kwargs):
        super(ExamenClasificacionForm, self).__init__(*args, **kwargs)
        self.fields['idioma'].queryset = Idioma.objects.all().order_by('nombre')
        self.fields['docentes_evaluadores'].queryset = Docente.objects.all().order_by('persona__primer_nombre')

    def clean(self):
        cleaned_data = super(ExamenClasificacionForm, self).clean()
        nuevo_inicial = cleaned_data.get('cupo_inicial')
        nuevo_autorizado = cleaned_data.get('cupo_autorizado')

        if self.instance:
            if nuevo_inicial > self.instance.cupo_inicial:
                self.instance.cupo_disponible += nuevo_inicial - self.instance.cupo_inicial

            if nuevo_autorizado > self.instance.cupo_autorizado:
                self.instance.cupo_disponible_autorizado += nuevo_autorizado - self.instance.cupo_autorizado


        return cleaned_data

class SeleccionarIdiomaForm(forms.Form):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all())
