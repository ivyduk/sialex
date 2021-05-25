from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms

from ..models import InformacionPreinscripcionFormalizacion


class MensajeFormalizacionForm(forms.ModelForm):
    class Meta:
        model = InformacionPreinscripcionFormalizacion
        exclude = ['periodo']