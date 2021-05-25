from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..forms.PagoBancoForm import PagoBancoForm, PagoBancoFormUpdate
from ..models import ComprobanteBanco, Preinscripcion, PreinscripcionHorarioCurso, PreinscripcionExamen
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from bootstrap_modal_forms.generic import BSModalUpdateView

class ComprobantePagoCreateView(LoginRequiredMixin,CreateView):
    template_name = 'administracion/comprobanteBanco/comprobante_banco_form.html'
    form_class = PagoBancoForm
    success_message = 'Exitoso: Pago fue agregado correctamente.'
    preinscripcion = None
    tipo = None

    def get_context_data(self,**kwargs):
        context = super(ComprobantePagoCreateView, self).get_context_data(**kwargs)
        self.preinscripcion = Preinscripcion.objects.get(id=kwargs['preinscripcionhorariocurso'])
        context['preinscripcion'] = self.preinscripcion
        return context
    
    def get(self, request, *args, **kwargs):
        data = dict()
        form = PagoBancoForm()
        self.preinscripcion = Preinscripcion.objects.get(id=kwargs['preinscripcionhorariocurso'])
        context = {'form': form, 'preinscripcion' : self.preinscripcion}
        data['html_form'] = render_to_string('administracion/comprobanteBanco/comprobante_banco_form.html',
        context,request=request)
        return JsonResponse(data)


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.periodo_generado_id = self.request.session["periodo_contextualizado_id"]
        self.preinscripcion = Preinscripcion.objects.get(id=self.kwargs['preinscripcionhorariocurso'])
        self.object.beneficiario = self.preinscripcion.persona
        self.object.preinscripcion_generada = self.preinscripcion
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        data = dict()
        data['form_is_valid'] = False
        preinscripcion = Preinscripcion.objects.get(id=kwargs['preinscripcionhorariocurso'])
        context = {'form': form, 'preinscripcion' : preinscripcion}
        data['html_form'] = render_to_string('administracion/comprobanteBanco/comprobante_banco_form.html',
        context,request=request)
        return JsonResponse(data)

    def get_success_url(self):
        try:
            examen = PreinscripcionExamen.objects.get(id=self.object.preinscripcion_generada_id)
        except PreinscripcionExamen.DoesNotExist:
            examen = None
        if examen:
            return reverse_lazy('formalizar-examen', kwargs={'pk': self.object.preinscripcion_generada_id})
        else:
            return reverse_lazy('formalizar-curso', kwargs={'pk': self.object.preinscripcion_generada_id})

class ComprobantePagoUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = ComprobanteBanco
    template_name = 'administracion/comprobanteBanco/comprobante_banco_update.html'
    form_class = PagoBancoFormUpdate
    success_message = 'Actualizados Pagos Banco.'

    def get_success_url(self):
        try:
            examen = PreinscripcionExamen.objects.get(id=self.object.preinscripcion_generada_id)
        except PreinscripcionExamen.DoesNotExist:
            examen = None
        if examen:
            return reverse_lazy('formalizar-examen', kwargs={'pk': self.object.preinscripcion_generada_id})
        else:
            return reverse_lazy('formalizar-curso', kwargs={'pk': self.object.preinscripcion_generada_id})
            