from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from ..forms.inscripcionForm import ObservacionPreinscripcionForm
from ..models import Preinscripcion, PreinscripcionExamen


class ObservacionesUpdateView(LoginRequiredMixin, UpdateView):
    model = Preinscripcion
    template_name = 'administracion/preinscripcionObservaciones/preinscripcion_observaciones_update.html'
    form_class = ObservacionPreinscripcionForm
    success_message = 'Actualizadas Observaciones.'

    def get_success_url(self):
        try:
            examen = PreinscripcionExamen.objects.get(id=self.object.id)
        except PreinscripcionExamen.DoesNotExist:
            examen = None
        if examen:
            return reverse_lazy('formalizar-examen', kwargs={'pk': self.object.id})
        else:
            return reverse_lazy('formalizar-curso', kwargs={'pk': self.object.id})








