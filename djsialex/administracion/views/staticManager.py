from django.shortcuts import render
from django.views.generic import TemplateView

from ..models import Periodo

class AboutPageView(TemplateView):
    template_name = 'administracion/about.html'

class HomePageView(TemplateView):
    template_name = 'administracion/home.html'

