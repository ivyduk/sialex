from bootstrap_datepicker_plus import DateTimePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from django import forms
from datetime import datetime
import pytz

from administracion.models import FallaAsistencia

class FallaAsistenciaForm(forms.ModelForm):

    class Meta:
        model = FallaAsistencia
        exclude = ['matricula', 'persona_asignadora']

        labels = {
            'fecha': 'Fecha (aaaa-mm-dd)',
            'cantidad_fallas': 'Número inasistencias'
        }

    def __init__(self, *args, **kwargs):
        super(FallaAsistenciaForm, self).__init__(*args, **kwargs)
        self.fields['cantidad_fallas'].widget.attrs['min'] = 1


class FallaAsistenciaUpdateForm(BSModalForm):

    class Meta:
        model = FallaAsistencia
        exclude = ['matricula', 'persona_asignadora']

        labels = {
            'fecha': 'Fecha (aaaa-mm-dd)',
            'cantidad_fallas': 'Número inasistencias'
        }

    def __init__(self, *args, **kwargs):
        super(FallaAsistenciaUpdateForm, self).__init__(*args, **kwargs)
        self.fields['cantidad_fallas'].widget.attrs['min'] = 1