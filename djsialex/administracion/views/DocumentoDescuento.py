from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..forms.DocumentosDescuentoSolicitadoForm import DocumentosDescuentoSolicitadoForm
from ..models import DocumentosDescuentoSolicitado
from bootstrap_modal_forms.generic import BSModalUpdateView
from django.http import HttpResponseRedirect

# Update
class DocumentoDescuentoUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = DocumentosDescuentoSolicitado
    template_name = 'administracion/documentoDescuentoSolicitado/documento_descuento_form.html'
    form_class = DocumentosDescuentoSolicitadoForm
    success_message = 'Actualizados documentos de descuento.'


    def get_success_url(self):
        return reverse_lazy('formalizar-curso', kwargs={'pk': self.object.descuento_aplicado.preinscripcion_generada_id})
