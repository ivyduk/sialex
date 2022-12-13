from bootstrap_datepicker_plus import DateTimePickerInput
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..models import reporteHermes_conf,Preinscripcion, PreinscripcionHorarioCurso, Periodo
from ..forms.ReporteFechaForm import ReporteFechaForm

from django.contrib import messages
from ..models import DatosEstudiantesModel
from django.contrib.auth.decorators import login_required
from ..serialize import DatosEstudiantesSerialize
from rest_framework import viewsets
from django.shortcuts import render, redirect

from administracion.util import CSVWriter
from administracion.models import getEstadoPreinscripcion

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
            if fechafinal < fechainicio:
                form.add_error('fecha_final', 'La fecha final no puede ser menor a la fecha de inicio')
                return render(request, template_name, {'form':form})   
            else:
               form.save()
               messages.add_message(request, messages.SUCCESS,'Se ha modificado la configuracion del reporte HERMES')
               return redirect('reporte_hermes')

@login_required
def descargarReporteHermes(request):

    periodo_id = request.session["periodo_contextualizado_id"]
    periodo = Periodo.objects.get(pk=periodo_id)

    preinscripcion = PreinscripcionHorarioCurso.objects.filter(
        horario_cupo__curso__oferta_academica__periodo=periodo
    )

    data = {i+1: [preinscripcion[i].persona.tipo_documento,
                  preinscripcion[i].persona.numero_documento, preinscripcion[i].persona.getNombreCompleto().upper(),
                  preinscripcion[i].persona.usuario.email, getEstadoPreinscripcion(preinscripcion[i].estado_preinscripcion),
                  preinscripcion[i].horario_cupo.nombre,
                  preinscripcion[i].fecha_preinscripcion.strftime('%d/%m/%Y - %H:%M'), preinscripcion[i].valor_preinscripcion]
             for i in range(len(preinscripcion))}

    header = ['#', 'Tipo documento', 'Numero documento', 'Nombre estudiante', 'Correo electrónico', 'Estado',
              "Curso", 'Fecha Inscripcion', 'Valor inscripcion']

    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, 'Preinscritos-' + str(periodo.alias))
    return response

class DatosEstudiantesAPI(viewsets.ModelViewSet):
    config = reporteHermes_conf.objects.first()
    fechainicio = config.fecha_inicio
    fechafinal = config.fecha_final
    queryset = DatosEstudiantesModel.objects.raw('select * from datosEstudiantes(\'{}\',\'{}\')'.format(fechainicio,fechafinal))
    serializer_class = DatosEstudiantesSerialize
