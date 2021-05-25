from django.db.models import Max
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from administracion.forms.nivelForm import NivelForm
from ..models import Nivel, ContenidoNivel, ContenidoNivelVersion


class NivelListView(LoginRequiredMixin, generic.ListView):
    model = Nivel
    template_name = 'administracion/nivel/nivel_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        nivel_list = Nivel.objects.filter().all().order_by('idioma__nombre','orden', 'alias')
        return nivel_list

class NivelDetailView(LoginRequiredMixin,generic.DetailView):
    model = Nivel
    template_name = 'administracion/nivel/nivel_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super(NivelDetailView, self).get_context_data(**kwargs)
        nivel = self.object
        if nivel.contenido:
            version_contenido = ContenidoNivelVersion.objects.filter(contenido_nivel=nivel.contenido).aggregate(max=Max('version'))['max']
            ultima_version_contenido = ContenidoNivelVersion.objects.filter(contenido_nivel=nivel.contenido, version=version_contenido).first()
            context['contenido_nivel'] = ultima_version_contenido
        return context

class NivelCreate(LoginRequiredMixin, CreateView):
    form_class = NivelForm
    template_name = 'administracion/nivel/nivel_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.contenido_id is None:
            self.object.contenido = ContenidoNivel.objects.create(alias='contenido-' + self.object.alias, version_actual=0)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        return reverse_lazy('nivel-detail', kwargs={'pk': self.object.id})


class NivelUpdate(LoginRequiredMixin, UpdateView):
    model = Nivel
    template_name = 'administracion/nivel/nivel_form.html'
    fields = '__all__'

class NivelDelete(LoginRequiredMixin, DeleteView):
    model = Nivel
    template_name = 'administracion/nivel/nivel_confirm_delete.html'
    success_url = reverse_lazy('niveles')
