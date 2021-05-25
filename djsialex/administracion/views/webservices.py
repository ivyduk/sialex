from typing import re
import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json

from ..models import Pais, Region, Ciudad, Nivel, Salon


@login_required
def webservice_desplegable_paises(request):
    error = False
    if request.user.is_authenticated:
        paises= Pais.objects.filter().all();
        data={}
        for i in paises:
            data[str(i.id)] = i.nombre
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def webservice_desplegable_regiones(request):
    error = False
    if request.user.is_authenticated:
        parent_id = request.GET.get('parent')
        regiones = Region.objects.filter(pais=parent_id).all();
        data = {}
        for i in regiones:
            data[str(i.id)] = i.nombre
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def webservice_desplegable_ciudades(request):
    error = False
    if request.user.is_authenticated:
        parent_id = request.GET.get('parent')
        ciudades = Ciudad.objects.filter(region=parent_id).all();
        data = {}
        for i in ciudades:
            data[str(i.id)] = i.nombre
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def webservice_pais_region_ciudad(request):
    error = False
    if request.user.is_authenticated:
        child_id = request.GET.get('child')
        ciudad = Ciudad.objects.get(pk=child_id);
        region = Region.objects.get(pk=ciudad.region.id);
        data = {}
        data['region'] = ciudad.region.id
        data['pais'] = region.pais.id
        serialized_obj = json.dumps(data)
        return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})

@login_required
def webservice_niveles_idioma(request):
    error = False
    if request.user.is_authenticated:
        lang = request.GET.get('idioma')
        if lang != '':
            levels = Nivel.objects.filter(idioma__id=lang).all();
            data = {}
            for i in levels:
                data[str(i.id)] = i.alias
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})


@login_required
def webservice_salones_edificio(request):
    if request.user.is_authenticated:
        edificio = request.GET.get('edificio')
        if edificio != '':
            salones = Salon.objects.filter(edificio__id=edificio).all()
            data = {}
            for i in salones:
                data[str(i.id)] = i.nombre
            serialized_obj = json.dumps(data)
            return render(request, 'webservices/index.html', {'resultset': serialized_obj})
    return render(request, 'webservices/error.html', {'resultset': "Error de autenticación"})