from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from administracion.forms import ContenidoNivelVersionForm, ContenidoNivelVersionFormUpdate
from ..models import ContenidoNivelVersion, ContenidoNivel
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.template.loader import render_to_string

class ContenidoNivelVersionCreateView(LoginRequiredMixin,CreateView):
    template_name = 'administracion/contenidoNivelVersion/contenidonivel_version_form.html'
    form_class = ContenidoNivelVersionForm
    success_message = 'Nueva Version al contenido fue subida.'

    def get_context_data(self, **kwargs):
        context = super(ContenidoNivelVersionCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['contenidonivelversion_form'] = ContenidoNivelVersionForm(self.request.POST, self.request.FILES)
        else:
            context['contenidonivelversion_form'] = ContenidoNivelVersionForm()
        return context

    def get(self, request, *args, **kwargs):
        data = dict()
        form = ContenidoNivelVersionForm()
        contenidonivel = ContenidoNivel.objects.get(id=self.kwargs['contenidonivel'])
        context = {'form': form, 'contenidonivel': contenidonivel.id}
        data['html_form'] = render_to_string('administracion/contenidoNivelVersion/contenidonivel_version_form.html',
        context, request=request)
        return JsonResponse(data)

    def form_valid(self, form):
        context = self.get_context_data()
        contenidonivelversion_form = context['contenidonivelversion_form']
        if contenidonivelversion_form.is_valid():
            self.object = form.save(commit=False)
            contenidonivel = ContenidoNivel.objects.get(id=self.kwargs['contenidonivel'])
            self.object.contenido_nivel_id = contenidonivel.id
            if self.object.documento:
                version = contenidonivel.version_actual
                versionnueva = version + 1
                ContenidoNivel.objects.filter(pk=contenidonivel.id).update(version_actual=versionnueva)
                self.object.version = versionnueva
            return super(ContenidoNivelVersionCreateView,self).form_valid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('contenido-nivel-detail', kwargs={'pk': self.object.contenido_nivel_id})



# Update
class ContenidoNivelVersionUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = ContenidoNivelVersion
    template_name = 'administracion/contenidoNivelVersion/contenidonivel_version_update.html'
    form_class = ContenidoNivelVersionFormUpdate
    success_message = 'Nueva Version al contenido fue actualizada.'

    def form_valid(self, form):
        context = self.get_context_data()
        contenidonivelversion_form = context['contenidonivelversionupdate_form']
        if contenidonivelversion_form.is_valid():
            self.object = form.save(commit=False)
            return super(ContenidoNivelVersionUpdateView, self).form_valid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('contenido-nivel-detail', kwargs={'pk': self.object.contenido_nivel_id})

    def get_context_data(self, **kwargs):
        context = super(ContenidoNivelVersionUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['contenidonivelversionupdate_form'] = ContenidoNivelVersionFormUpdate(self.request.POST, self.request.FILES)
        else:
            context['contenidonivelversionupdate_form'] = ContenidoNivelVersionFormUpdate()
        return context