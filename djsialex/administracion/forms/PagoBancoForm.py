from django import forms

from ..models import ComprobanteBanco
from bootstrap_modal_forms.forms import BSModalForm

class PagoBancoForm(forms.ModelForm):
    valor = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            "min": 0,
            'oninput': "validity.valid||(value='');"
        }
    )
    )
    
    class Meta:
        model = ComprobanteBanco
        exclude = ['beneficiario', 'periodo_generado', 'preinscripcion_generada', 'estado_pago', 'tipo']

class PagoBancoFormUpdate(BSModalForm):
    valor = forms.FloatField(widget=forms.NumberInput(attrs={"min": 0, 'oninput': "validity.valid||(value='');"}))
    
    class Meta:
        model = ComprobanteBanco
        exclude = ['beneficiario', 'periodo_generado', 'preinscripcion_generada', 'estado_pago', 'tipo']