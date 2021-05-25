from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import OfertaAcademica, Descuento
from ..forms.ofertaForms import OfertaAcademicaCreateForm

class OfertaAcademicaListView(LoginRequiredMixin, generic.ListView):
    model = OfertaAcademica
    template_name = 'administracion/ofertaAcademica/oferta_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class OfertaAcademicaDetailView(LoginRequiredMixin,generic.DetailView):
    model = OfertaAcademica
    template_name = 'administracion/ofertaAcademica/oferta_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class OfertaAcademicaCreate(LoginRequiredMixin, CreateView):
    model = OfertaAcademica
    form_class = OfertaAcademicaCreateForm
    template_name = 'administracion/ofertaAcademica/oferta_form.html'

    def get_form(self, *args, **kwargs):
        form = super(OfertaAcademicaCreate, self).get_form(*args, **kwargs)
        form.fields['descuentos'].queryset = Descuento.objects.filter(activo=True)
        return form

class OfertaAcademicaUpdate(LoginRequiredMixin, UpdateView):
    model = OfertaAcademica
    form_class = OfertaAcademicaCreateForm
    template_name = 'administracion/ofertaAcademica/oferta_form.html'

    def get_form(self, *args, **kwargs):
        form = super(OfertaAcademicaUpdate, self).get_form(*args, **kwargs)
        form.fields['descuentos'].queryset = Descuento.objects.filter(activo=True)
        return form

class OfertaAcademicaDelete(LoginRequiredMixin, DeleteView):
    model = OfertaAcademica
    template_name = 'administracion/ofertaAcademica/oferta_confirm_delete.html'
    success_url = reverse_lazy('ofertas')