from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse_lazy

from ..forms.mensajeFormalizacionForm import MensajeFormalizacionForm
from ..models import InformacionPreinscripcionFormalizacion

class MensajeFormalizacionCreate(LoginRequiredMixin, CreateView):
    model = InformacionPreinscripcionFormalizacion
    template_name = 'administracion/configuracion/mensaje_formalizacion_form.html'
    form_class = MensajeFormalizacionForm
    success_url = reverse_lazy('mensajeformalizacion_list')

class MensajeFormalizacionUpdate(LoginRequiredMixin, UpdateView):
    model = InformacionPreinscripcionFormalizacion
    template_name = 'administracion/configuracion/mensaje_formalizacion_form.html'
    form_class = MensajeFormalizacionForm
    success_url = reverse_lazy('mensajeformalizacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.object
        context['periodo'] = instance.periodo
        return context

class MensajeFormalizacionList(LoginRequiredMixin, ListView):
    model = InformacionPreinscripcionFormalizacion
    template_name = 'administracion/configuracion/mensaje_formalizacion_list.html'
    success_url = reverse_lazy('mensajeformalizacion_list')

    def get_queryset(self):
        mensajes_list = InformacionPreinscripcionFormalizacion.objects.filter(periodo_id = self.request.session["periodo_contextualizado_id"]).all()
        return mensajes_list