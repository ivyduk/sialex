from django import forms

from ..models import PreinscripcionHorarioCurso


class DescuentoSolicitadoForm(forms.ModelForm):

    class Meta:
        model = PreinscripcionHorarioCurso
        fields = ['descuento_solicitado']