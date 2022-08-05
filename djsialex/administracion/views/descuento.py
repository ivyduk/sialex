from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect

from ..models import Descuento, DescuentoAplicado, PreinscripcionHorarioCurso, DocumentosDescuentoSolicitado
from ..forms import DescuentoAplicadoForm, DescuentoSolicitadoForm


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

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('formalizar-curso',
                            kwargs={'pk': self.object.id})

class CrearDescuento(LoginRequiredMixin, UpdateView):
    model = PreinscripcionHorarioCurso
    form_class = DescuentoSolicitadoForm
    template_name = 'administracion/inscripcion/descuento_confirm_create.html'
    success_url = reverse_lazy('buscar-preinscripciones')

    def form_valid(self, form):
        nuevo_descuento = form.data['descuento_solicitado']
        if nuevo_descuento:
            descuento = Descuento.objects.get(pk=int(nuevo_descuento))
        else:
            descuento = None
        if not descuento:
            messages.warning(self.request, 'Se requiere seleccionar al menos un descuento')
            return redirect(reverse('descuento_aplicado_editar', kwargs={'pk': self.object.id}))
        else:
            
            self.object.valor_preinscripcion = 660000
            self.object.save()

            valor_descuento = (self.object.valor_preinscripcion * descuento.porcentaje) / 100
            self.object.valor_preinscripcion -= valor_descuento
            self.object.descuento_id=nuevo_descuento
            self.object.save()
            
            periodo = periodo.objects.get(pk=self.request.session["periodo_contextualizado_id"])
            descuento_solicitado = DescuentoAplicado(
                    beneficiario=self.object.persona,
                    periodo_generado=periodo,
                    valor=self.object.valor_preinscripcion - valor_descuento,
                    descuento_id=nuevo_descuento,
                    preinscripcion_generada=self.object
                )
            descuento_solicitado.save()
        


            """    for doc in descuento.descuento.documentos_requeridos.filter(activo=True):
                    documento_descuento = DocumentosDescuentoSolicitado(
                        descuento_aplicado=descuento,
                        documento_requerido=doc
                    )
                    documento_descuento.save()
            except DescuentoAplicado.ValidationError:
                pass
            """
            
            #for doc in descuento.documentos_requeridos.filter(activo=True):
            #    documento_descuento = DocumentosDescuentoSolicitado(
            #        descuento_aplicado=descuento.id,
            #        documento_requerido=doc
            #    )
            #    documento_descuento.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('formalizar-curso',
                            kwargs={'pk': self.object.id})

class ModificarDescuento(LoginRequiredMixin, UpdateView):
    model = DescuentoAplicado
    form_class = DescuentoAplicadoForm
    template_name = 'administracion/inscripcion/descuento_confirm_update.html'
    success_url = reverse_lazy('buscar-preinscripciones')

    def form_valid(self, form):
        nuevo_descuento = form.data['descuento']
        if nuevo_descuento:
            descuento = Descuento.objects.get(pk=int(nuevo_descuento))
        else:
            descuento = None
        if not descuento:
            messages.warning(self.request, 'Se requiere seleccionar al menos un descuento')
            return redirect(reverse('descuento_aplicado_editar', kwargs={'pk': self.object.id}))
        else:
            anterior_valor = self.object.valor
            self.object.preinscripcion_generada.valor_preinscripcion += anterior_valor
            self.object.preinscripcion_generada.save()

            valor_descuento = (self.object.preinscripcion_generada.valor_preinscripcion * descuento.porcentaje) / 100
            self.object.preinscripcion_generada.valor_preinscripcion -= valor_descuento
            self.object.preinscripcion_generada.save()
            self.object.valor = valor_descuento
            self.object.descuento_solicitado = descuento
            self.object.save()
            documentos_descuento = DocumentosDescuentoSolicitado.objects.filter(descuento_aplicado=self.object.id)
            for doc in documentos_descuento:
                doc.delete()
            for doc in descuento.documentos_requeridos.filter(activo=True):
                documento_descuento = DocumentosDescuentoSolicitado(
                    descuento_aplicado=self.object,
                    documento_requerido=doc
                )
                documento_descuento.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        descuento_aplicado = DescuentoAplicado.objects.get(id=self.kwargs["pk"])
        return reverse_lazy('formalizar-curso',
                            kwargs={'pk': descuento_aplicado.preinscripcion_generada_id})