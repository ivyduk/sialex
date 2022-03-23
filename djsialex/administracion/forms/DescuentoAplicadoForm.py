from django import forms

from ..models import DescuentoAplicado


class DescuentoAplicadoForm(forms.ModelForm):

    class Meta:
        model = DescuentoAplicado
        fields = ['descuento']
