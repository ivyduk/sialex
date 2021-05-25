from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ..models import Url

class UrlListView(LoginRequiredMixin, generic.ListView):
    model = Url
    template_name = 'administracion/url/url_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class UrlDetailView(LoginRequiredMixin,generic.DetailView):
    model = Url
    template_name = 'administracion/url/url_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class UrlCreate(LoginRequiredMixin, CreateView):
    model = Url
    template_name = 'administracion/url/url_form.html'
    fields = '__all__'

class UrlUpdate(LoginRequiredMixin, UpdateView):
    model = Url
    template_name = 'administracion/url/url_form.html'
    fields = '__all__'

class UrlDelete(LoginRequiredMixin, DeleteView):
    model = Url
    template_name = 'administracion/url/url_confirm_delete.html'
    success_url = reverse_lazy('urls')