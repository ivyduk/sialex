from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..forms.EventoPeriodoForm import EventoPeriodoForm
from ..models import EventoPeriodo

class EventoPeriodoListView(LoginRequiredMixin, generic.ListView):
    model = EventoPeriodo
    template_name = 'administracion/eventoPeriodo/eventoperiodo_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        periodo_actual_id = self.request.session["periodo_contextualizado_id"]
        eventoperiodo_list = EventoPeriodo.objects.filter(periodo_id=periodo_actual_id)
        return eventoperiodo_list

class EventoPeriodoDetailView(LoginRequiredMixin,generic.DetailView):
    model = EventoPeriodo
    template_name = 'administracion/eventoPeriodo/eventoperiodo_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class EventoPeriodoCreate(LoginRequiredMixin, CreateView):
    template_name = 'administracion/eventoPeriodo/eventoperiodo_form.html'
    form_class = EventoPeriodoForm

class EventoPeriodoUpdate(LoginRequiredMixin, UpdateView):
    model = EventoPeriodo
    template_name = 'administracion/eventoPeriodo/eventoperiodo_form.html'
    form_class = EventoPeriodoForm

    def get_initial(self):
        super(EventoPeriodoUpdate, self).get_initial()
        periodo_actual_id = self.request.session["periodo_contextualizado_id"]
        self.initial = {"periodo": periodo_actual_id}
        return self.initial

class EventoPeriodoDelete(LoginRequiredMixin, DeleteView):
    model = EventoPeriodo
    template_name = 'administracion/eventoPeriodo/eventoperiodo_confirm_delete.html'
    success_url = reverse_lazy('eventosPeriodo')