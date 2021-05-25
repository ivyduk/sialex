from django import forms

from ..models import Devolucion

class DevolucionForm(forms.ModelForm):
    porcentaje = forms.FloatField( widget=forms.NumberInput(attrs={"min" : 0, 'max' : '100', 'oninput': "validity.valid||(value='');"}), label='Porcentaje a devolver')

    class Meta:
        model = Devolucion
        fields = [
            'porcentaje',
            'observacion',
        ]