from django.forms import  Form
from django import forms

from ..models import PreinscripcionHorarioCurso


class AplazarCursoForm(Form):
    CHOICES = [(2, 'Motivo usuario'),
               (4, 'Motivo departamento')]

    motivo = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=True)
    valor_saldo_a_favor = forms.FloatField(
        label='Valor a cargar como saldo a favor del usuario',
        widget=forms.NumberInput(attrs={"min": 0, 'oninput': "validity.valid||(value='');"})
    )

    def clean(self):
        cleaned_data = super(AplazarCursoForm, self).clean()


class AplazarExamenForm(Form):
    CHOICES = [(2, 'Motivo usuario'),
               (4, 'Motivo departamento')]

    motivo = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, required=True)
    valor_saldo_a_favor = forms.FloatField(
        label='Valor a cargar como saldo a favor del usuario',
        widget=forms.NumberInput(attrs={"min": 0, 'oninput': "validity.valid||(value='');"})
    )

    def clean(self):
        cleaned_data = super(AplazarExamenForm, self).clean()