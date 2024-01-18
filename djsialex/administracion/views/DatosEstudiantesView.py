from bootstrap_datepicker_plus import DateTimePickerInput
from ..models import ReporteHermesConfiguracion
from ..forms.ReporteFechaForm import ReporteFechaForm
from django.contrib import messages
from ..models import DatosEstudiantesModel
from django.contrib.auth.decorators import login_required
from ..serialize import DatosEstudiantesSerialize
from rest_framework import viewsets
from django.shortcuts import render, redirect
from administracion.util import CSVWriter


@login_required
def escogerOpcionReportes(request):

    return render(request, 'administracion/reportes/reportes_opciones.html')

@login_required
def fechaOpcionReportes(request):
        return render(request, 'administracion/reportes/reportes_fechas.html')

@login_required
def reporteFechaCreate(request):
    template_name = 'administracion/reportes/reportes_fechas.html'
    config = ReporteHermesConfiguracion.objects.first()

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


def descargarReporteHermes(request):
    config = ReporteHermesConfiguracion.objects.first()
    fechainicio = config.fecha_inicio
    fechafinal = config.fecha_final
    estudiante = DatosEstudiantesModel.objects.raw('select * from datosEstudiantes(\'{}\',\'{}\')'.format(fechainicio,fechafinal))

    data = {}
    for i in range(len(estudiante)):

        data_calificacion = [estudiante[i].id_sub_proyecto_curso, estudiante[i].tipo_documento, estudiante[i].numero_documento,
                             estudiante[i].primer_nombre, estudiante[i].segundo_nombre, estudiante[i].primer_apellido,
                             estudiante[i].segundo_apellido, estudiante[i].sexo_biologico, estudiante[i].estado_civil,
                             estudiante[i].fecha_nacimiento, estudiante[i].pais_nacimiento, estudiante[i].departamento_nacimiento,
                             estudiante[i].ciudad_nacimiento, estudiante[i].nivel_formacion, estudiante[i].egresado_un,
                             estudiante[i].vinculacion, estudiante[i].telefono_fijo, estudiante[i].ext, estudiante[i].celular,
                             estudiante[i].email, estudiante[i].direccion_residencia, estudiante[i].pais_residencia,
                             estudiante[i].departamento_residencia, estudiante[i].ciudad_residencia, estudiante[i].descuento,
                             estudiante[i].valor_inscripcion, estudiante[i].valor_pago, estudiante[i].fecha_pago,
                             estudiante[i].no_soporte_de_pago, estudiante[i].tipo_pago, estudiante[i].tarifa_materiales]
        data[i+1] = data_calificacion

    header = [
        '#',
        'id_sub_proyecto_curso',
        'tipo_documento',
        'numero_documento',
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'sexo_biologico',
        'estado_civil',
        'fecha_nacimiento',
        'pais_nacimiento',
        'departamento_nacimiento',
        'ciudad_nacimiento',
        'nivel_formacion',
        'egresado_un',
        'vinculacion',
        'telefono_fijo',
        'ext',
        'celular',
        'email',
        'direccion_residencia',
        'pais_residencia',
        'departamento_residencia',
        'ciudad_residencia',
        'descuento',
        'valor_inscripcion',
        'valor_pago',
        'fecha_pago',
        'no_soporte_de_pago',
        'tipo_pago',
        'tarifa_materiales'
    ]
    csv_writer = CSVWriter()
    response = csv_writer.download_csv_file(data, header, 'Reporte-{}-{}'.format(fechainicio, fechafinal))
    return response


class DatosEstudiantesAPI(viewsets.ModelViewSet):
    config = ReporteHermesConfiguracion.objects.first()
    fechainicio = config.fecha_inicio
    fechafinal = config.fecha_final
    queryset = DatosEstudiantesModel.objects.raw(
        'select * from datosEstudiantes(\'{}\',\'{}\')'.format(
            fechainicio, fechafinal
        )
    )
    serializer_class = DatosEstudiantesSerialize

