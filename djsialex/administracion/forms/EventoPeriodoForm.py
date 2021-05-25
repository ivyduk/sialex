from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms

from ..models import EventoPeriodo


class EventoPeriodoForm(forms.ModelForm):
    class Meta:
        model = EventoPeriodo
        fields = '__all__'

        FORMAT = '%Y-%m-%d %H:%M'
        widgets = {'fecha_inicio': DateTimePickerInput(format=FORMAT,), 'fecha_final': DateTimePickerInput(format=FORMAT),}
