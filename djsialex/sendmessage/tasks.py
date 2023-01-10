from __future__ import absolute_import, unicode_literals
from celery import shared_task 
import csv
import codecs, io
from django.core.mail import EmailMessage

from administracion.models import Periodo, PreinscripcionHorarioCurso
from datetime import date
from administracion.models import getEstadoPreinscripcion

@shared_task()
def Inscritos_Pendientes():
    print("Se ejecuta la tarea")
    periodos = Periodo.objects.filter(
        activo=True,
        finalizado=False,
        fecha_pendientes="2023-03-04" #date.today()
    )
    if periodos:
        print("Existen periodos para la generacion del Archivo")
        pendientes = PreinscripcionHorarioCurso.objects.filter(
            estado_preinscripcion=3,
            horario_cupo__curso__oferta_academica__periodo__in=periodos
        )
        header = ['#', 'Horario Curso', 'Tipo documento', 'Numero documento', 'Nombre estudiante',
                  'E-mail', 'Estado', 'Fecha Inscripcion', 'Valor inscripcion']
        data = {i+1: [pendientes[i].horario_cupo.nombre,pendientes[i].persona.tipo_documento,
                      pendientes[i].persona.numero_documento, pendientes[i].persona.getNombreCompleto().upper(),
                      pendientes[i].persona.usuario.email, getEstadoPreinscripcion(pendientes[i].estado_preinscripcion),
                      pendientes[i].fecha_preinscripcion.strftime('%d%m%Y'), pendientes[i].valor_preinscripcion]
                for i in range(len(pendientes))}

        csvfile = io.BytesIO()
        StreamWriter = codecs.getwriter('utf-8')
        wrapper_file = StreamWriter(csvfile)
        writer = csv.writer(wrapper_file, csv.excel)

        writer.writerow([title for title in header])

        for d in data:
            writer.writerow([d] + data[d])

        fechaArchivo = date.today().strftime('%d%m%Y')
        nombreArchivo = 'PreInscritos_Pendientes_' + fechaArchivo + '.csv'

        email = EmailMessage(
        'PreInscritos Pendientes',
        'Buen Dia!! Se adjunta el archivo con los preinscritos en estado pendiente.',
        'sialex_fchbog@unal.edu.co',
        ['ivanduquecs@gmail.com','roprale@gmail.com']
        )
        print("Se envia el correo")
        email.attach(nombreArchivo, csvfile.getvalue(), 'text/csv')
        email.send()
