from bootstrap_datepicker_plus import DateTimePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from django import forms
from datetime import datetime
import pytz

from administracion.models import FallaAsistencia
from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput


class FallaAsistenciaForm(forms.ModelForm):

    class Meta:
        model = FallaAsistencia
        exclude = ['matricula', 'persona_asignadora']

        FORMAT = '%Y-%m-%d'
        widgets = {
            'fecha': DatePickerInput(format=FORMAT),
        }

        labels = {
            'fecha': 'Fecha inasistencia',
            'cantidad_fallas': 'Número inasistencias'
        }

    def __init__(self, *args, **kwargs):
        super(FallaAsistenciaForm, self).__init__(*args, **kwargs)
        self.fields['cantidad_fallas'].widget.attrs['min'] = 1


class FallaAsistenciaUpdateForm(BSModalForm):

    class Meta:
        model = FallaAsistencia
        exclude = ['matricula', 'persona_asignadora']

        FORMAT = '%Y-%m-%d'
        widgets = {
            'fecha': DatePickerInput(format=FORMAT),
        }

        labels = {
            'fecha': 'Fecha (aaaa-mm-dd)',
            'cantidad_fallas': 'Número inasistencias'
        }

    def __init__(self, *args, **kwargs):
        super(FallaAsistenciaUpdateForm, self).__init__(*args, **kwargs)
        self.fields['cantidad_fallas'].widget.attrs['min'] = 1