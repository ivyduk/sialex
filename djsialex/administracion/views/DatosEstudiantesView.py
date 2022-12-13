from bootstrap_datepicker_plus import DateTimePickerInput
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..models import reporteHermes_conf
from ..forms.ReporteFechaForm import ReporteFechaForm

from django.contrib import messages
from ..models import DatosEstudiantesModel
from django.contrib.auth.decorators import login_required
from ..serialize import DatosEstudiantesSerialize
from rest_framework import viewsets
from django.shortcuts import render, redirect

@login_required
def escogerOpcionReportes(request):
    
    return render(request, 'administracion/reportes/reportes_opciones.html')

@login_required
def fechaOpcionReportes(request):
        return render(request, 'administracion/reportes/reportes_fechas.html') 

@login_required
def reporteFechaCreate(request):
    template_name = 'administracion/reportes/reportes_fechas.html'
    config = reporteHermes_conf.objects.first()
    
    if request.method == "GET":
        fechainicio = config.fecha_inicio
        fechafinal = config.fecha_final
        initial = {'fecha_inicio':fechainicio, 'fecha_final': fechafinal}
        form = ReporteFechaForm(initial=initial)
        return render(request, template_name, {'form':form})
    else:
        form = ReporteFechaForm(request.POST)

        if form.is_valid():
            fechainicio = request.POST['fecha_inicio']
            fechafinal = request.POST['fecha_final']
            print(fechainicio)
            print(fechafinal)
            if fechafinal < fechainicio:
                form.add_error('fecha_final', 'La fecha final no puede ser menor a la fecha de inicio')
                return render(request, template_name, {'form':form})   
            else:
               form.save()
               messages.add_message(request, messages.SUCCESS,'Se ha modificado la configuracion del reporte HERMES')
               return redirect('reporte_hermes')

class DatosEstudiantesAPI(viewsets.ModelViewSet):
    config = reporteHermes_conf.objects.first()
    fechainicio = config.fecha_inicio
    fechafinal = config.fecha_final
    queryset = DatosEstudiantesModel.objects.raw('select * from datosEstudiantes(\'{}\',\'{}\')'.format(fechainicio,fechafinal))
    serializer_class = DatosEstudiantesSerialize
