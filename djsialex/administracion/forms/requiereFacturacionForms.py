from django import forms

from ..models import Preinscripcion


class RequiereFacturacionForm(forms.ModelForm):

    class Meta:
        model = Preinscripcion
        fields = [
            'requiere_facturacion',
        ]