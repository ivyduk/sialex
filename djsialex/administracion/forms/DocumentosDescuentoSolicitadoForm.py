from django import forms

from ..models import DocumentosDescuentoSolicitado
from bootstrap_modal_forms.forms import BSModalForm

class DocumentosDescuentoSolicitadoForm(BSModalForm):
    class Meta:
        model = DocumentosDescuentoSolicitado
        exclude = ['descuento_aplicado', 'documento_requerido']