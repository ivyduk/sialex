from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from ..forms.ObservacionPreinscripcionForms import ObservacionPreinscripcionForm 
from ..models import Preinscripcion
from django.core import serializers


@method_decorator(csrf_exempt, name='dispatch')
class ObservacionesCreateView(View):
    template_name = 'administracion/inscripcion/preinscripcion_observaciones.html'

    def get(self, request, preinscripcion_id):
        preinscripcion = get_object_or_404(Preinscripcion, pk=preinscripcion_id)
        form = ObservacionPreinscripcionForm()
        context = {'form': form, 'preinscripcion': preinscripcion, 'form_type': 'observaciones'}
        html_form = render(request, self.template_name, context).content.decode('utf-8')
        return JsonResponse({'success': True, 'html_form': html_form, 'form_type': 'observaciones'})

    def post(self, request, preinscripcion_id):
        preinscripcion = get_object_or_404(Preinscripcion, pk=preinscripcion_id)
        form = ObservacionPreinscripcionForm(request.POST)

        if form.is_valid():
            observacion_texto = form.cleaned_data['observaciones']
            preinscripcion.observaciones = observacion_texto
            preinscripcion.save()

            if request.is_ajax():
                success_url = reverse_lazy('formalizar-curso', kwargs={'pk': preinscripcion_id})

                # Serializa el objeto Preinscripcion para incluir el campo 'observaciones' en la respuesta JSON
                preinscripcion_json = serializers.serialize('json', [preinscripcion])[0]['fields']
                preinscripcion_json['observacion_texto'] = observacion_texto

                context = {'form': form, 'preinscripcion': preinscripcion, 'form_type': 'observaciones'}
                html_form = render(request, self.template_name, context).content.decode('utf-8')

                return JsonResponse({
                    'success': True,
                    'redirect_url': success_url,
                    'observacion_texto': observacion_texto,
                    'html_form': html_form,
                })
            else:
                return redirect('formalizar-curso', pk=preinscripcion_id)
        else:
            # Manejar el caso donde el formulario no es válido
            context = {'form': form, 'preinscripcion': preinscripcion}
            html_form = render(request, self.template_name, context).content.decode('utf-8')
            return JsonResponse({'success': False, 'html_form': html_form})










