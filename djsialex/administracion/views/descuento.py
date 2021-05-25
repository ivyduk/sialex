from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import Descuento, DescuentoAplicado, PreinscripcionHorarioCurso

from django.http import HttpResponseRedirect

class DescuentoListView(LoginRequiredMixin, generic.ListView):
    model = Descuento
    template_name = 'administracion/descuento/descuento_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class DescuentoDetailView(LoginRequiredMixin,generic.DetailView):
    model = Descuento
    template_name = 'administracion/descuento/descuento_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class DescuentoCreate(LoginRequiredMixin, CreateView):
    model = Descuento
    template_name = 'administracion/descuento/descuento_form.html'
    fields = '__all__'

class DescuentoUpdate(LoginRequiredMixin, UpdateView):
    model = Descuento
    template_name = 'administracion/descuento/descuento_form.html'
    fields = '__all__'

class DescuentoDelete(LoginRequiredMixin, DeleteView):
    model = Descuento
    template_name = 'administracion/descuento/descuento_confirm_delete.html'
    success_url = reverse_lazy('descuentos')

class CancelDescuento(LoginRequiredMixin, DeleteView):

    model = PreinscripcionHorarioCurso
    template_name = 'administracion/inscripcion/descuento_confirm_delete.html'
    success_url = reverse_lazy('buscar-preinscripciones')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.descuento_solicitado
        preinscripcion_id = self.object.id
        try:
            descuento_solicitado = DescuentoAplicado.objects.get(preinscripcion_generada_id=preinscripcion_id)
            if descuento_solicitado.estado_descuento == 1:
                descuento_solicitado.estado_descuento = 3
                descuento_solicitado.save()
                self.object.valor_preinscripcion += descuento_solicitado.valor
                self.object.save()
        except DescuentoAplicado.DoesNotExist:
            descuento_solicitado = None      
        return HttpResponseRedirect(self.get_success_url())