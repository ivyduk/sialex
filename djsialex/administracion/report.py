import json
import os

from PIL import Image
from captcha.models import randrange
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

import reportlab

from administracion.enums import *
pn = os.path.dirname(os.path.abspath(__file__))
reportlab.rl_config.TTFSearchPath.append(pn + "/fonts/")
pdfmetrics.registerFont(TTFont('unal_italic', 'AncizarSans-ExtraboldItalic_02042016.ttf'))
pdfmetrics.registerFont(TTFont('unal_simple', 'AncizarSans-LightItalic_02042016.ttf'))

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from django.http import HttpResponse




def funcion(report):

    d_matricula = report['matricula']
    d_grupo = d_matricula.grupo

    d_estudiante = d_matricula.estudiante
    d_calificaciones = report['calificaciones']
    d_docentes_especializados = report['docentes_especializados']

    d_docentes = report['docentes_generales']
    d_observaciones = report['observaciones']
    if len(d_docentes)>0:
        d_docentes=d_docentes[0]

    print()


    d_docentes=d_docentes.docente.persona
    nombre_docente =d_docentes.primer_nombre + " " + d_docentes.segundo_nombre  + " " +d_docentes.primer_apellido+ " " +d_docentes.segundo_apellido

    if len(d_docentes_especializados)>0:
        d_docentes_especializados=d_docentes_especializados[0]
        d_docentes_especializados = d_docentes_especializados.docente.persona
        nombre_docente_especializado = d_docentes_especializados.primer_nombre + " " + d_docentes_especializados.segundo_nombre + " " + d_docentes_especializados.primer_apellido + " " + d_docentes_especializados.segundo_apellido
    else:
        nombre_docente_especializado=''

    nombre_estudiante=d_estudiante.primer_nombre + " " + d_estudiante.segundo_nombre  + " " +d_estudiante.primer_apellido+ " " +d_estudiante.segundo_apellido

    calificaciones=[]
    for i in d_calificaciones:
        calificaciones.append({"label": i.nota.nombre, "percentage": str(i.nota.ponderacion), "grade": str(i.calificacion)})
    obs=""
    obs2 = "---"
    doc2 = "---"
    if len(d_observaciones)>0:
        for i in d_observaciones:
            if i.persona_asignadora in report['docentes']:
                if report['docentes'][i.persona_asignadora].tipo=="Geaneral":
                    obs=i.observacion
                else:
                    obs2 = i.observacion
                    doc2 = d_docentes[1].getNombreCompleto()


    filename = "/tmp/" + str(randrange(100)) + ".pdf"
    data = {
        "_sn": nombre_estudiante,
        "_tn": nombre_docente,
        "_lvl": d_grupo.nombre,

        "__grades": calificaciones,
        "__final": str(report['matricula'].calificacionFinal),
        "__abs": str(report['matricula'].total_fallas) + " de 12 horas permitidas",
        "__result": str(ESTADOS_ACADEMICOS_MATRICULA[d_matricula.estado_matricula-1][1]),
        "sp_cl": doc2,
        "cm_sp_cl": obs2,
        "cm_cl": obs,
        "__equivalences": [
            {"label": "---", "score": "---"},
        ]
    }

    width, height = letter
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_LEFT
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontName = 'unal_italic'
    styleN.fontName = 'unal_simple'
    styleNull = styles["BodyText"]
    styleNull.alignment = TA_CENTER
    styleNull.fontName = 'unal_simple'

    document_width, document_height = letter
    logo = "assets/cabecera_opt.png"
    signature = "assets/signature.png"
    Image_file = Image.open(logo)
    signature_file = Image.open(signature)
    image_width, image_height = Image_file.size
    signature_width, signature_height = signature_file.size
    image_aspect = signature_height / float(signature_width)
    signature_aspect = signature_height / float(signature_width)
    print_width = document_width
    print_height = document_width * image_aspect


    def coord(x, y, unit=1):
        x, y = x * unit, height - y * unit
        return x, y


    # StudentHeaders
    table_student_name = Paragraph('Nombre del estudiante:', styleN)
    table_teacher_name = Paragraph('Nombre del profesor:', styleN)
    table_level_name = Paragraph('Nivel:', styleN)
    # StudentData
    value_student_name = Paragraph(data['_sn'], styleBH)
    value_teacher_name = Paragraph(data['_tn'], styleBH)
    value_level_name = Paragraph(data['_lvl'], styleBH)

    # RecordsHeaders
    table_record_description = Paragraph('Descripción', styleBH)
    table_record_percentage = Paragraph('Porcentaje', styleBH)
    table_record_final = Paragraph('Nota final', styleBH)

    # NullRecord
    null_record = Paragraph('------', styleNull)
    # SummaryHeaders
    table_summary_final = Paragraph('Nota final', styleBH)
    table_summary_grade = Paragraph(data['__final'] + " - " + data['__result'], styleN)
    # SummaryData
    table_summary_absenteeism_label = Paragraph('Total inasistencias', styleBH)
    table_summary_absenteeism = Paragraph(data['__abs'], styleN)

    observations_label_1 = Paragraph('Nombre clase especializada - Profesor', styleBH)
    observations_label_2 = Paragraph('Observaciones clase especializada', styleBH)
    observations_label_3 = Paragraph('Observaciones clases de lengua', styleBH)

    __cm_1 = Paragraph(data["sp_cl"], styleN)
    __cm_2 = Paragraph(data["cm_sp_cl"], styleN)
    __cm_3 = Paragraph(data["cm_cl"], styleN)

    # Signature
    table_signature_label = Paragraph('Ligia Cortés Cárdenas<br />Coordinadora', styleBH)

    student_data = [
        [table_student_name, value_student_name],
        [table_teacher_name, value_teacher_name],
        [table_level_name, value_level_name]]

    summary_data = [
        [table_summary_final, table_summary_grade],
        [table_summary_absenteeism_label, table_summary_absenteeism]
    ]

    observations_data = [
        [observations_label_1],
        [__cm_1],
        [observations_label_2],
        [__cm_2],
        [observations_label_3],
        [__cm_3],

    ]

    signatures_data = [
        [table_signature_label],
    ]

    records_data = [
        [table_record_description, table_record_percentage, table_record_final],
    ]
    for i in range(len(data['__grades'])):
        __g = data['__grades'][i]
        records_data.append([Paragraph(__g['label'], styleNull), Paragraph(__g['percentage'] + "%", styleNull),
                             Paragraph(__g['grade'], styleNull)])

    student_table = Table(student_data, colWidths=[3.5 * cm, 12.4 * cm])
    records_table = Table(records_data, colWidths=[7.0 * cm, 2.5 * cm, 2.5 * cm])
    summary_table = Table(summary_data, colWidths=[6.95 * cm, 6.95 * cm])
    observations_table = Table(observations_data, colWidths=[16.9 * cm])
    signatures_table = Table(signatures_data, colWidths=[16.9 * cm])

    simple_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    records_table.setStyle(simple_style)
    summary_table.setStyle(simple_style)
    observations_table.setStyle(simple_style)
    student_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))


    c = canvas.Canvas(filename, pagesize=letter)

    c.drawImage(logo, document_width - print_width, document_height - print_height, width=print_width, height=print_height,
                mask='auto')

    c.drawImage(signature, 235, 70, 165, 30, mask='auto')
    c.setPageCompression(1)
    c.setAuthor("Universidad Nacional de Colombia")
    c.setTitle("Boletín de calificaciones")
    c.setAuthor("sialex framework")
    c.setProducer("sialex framework")
    c.setCreator("sialex framework")

    records_table.wrapOn(c, width, height)
    summary_table.wrapOn(c, width, height)
    student_table.wrapOn(c, width, height)
    signatures_table.wrapOn(c, width, height)
    observations_table.wrapOn(c, width, height)

    w, h = student_table.wrap(0, 0)
    yh = height - h - (5.5 * cm)
    yh_ = yh
    student_table.drawOn(c, (width - w) / 2, yh)

    w, h = records_table.wrap(0, 0)
    yh = yh - h - (0.5 * cm)
    yh_ = yh - h - (0.5 * cm)
    records_table.drawOn(c, (width - w - (0.5 * cm)) / 2, yh)

    w, h = summary_table.wrap(0, 0)
    yh = yh - h - (0.5 * cm)
    summary_table.drawOn(c, (width - w) / 2, yh)

    w, h = observations_table.wrap(0, 0)
    yh = yh - h - (0.5 * cm)
    observations_table.drawOn(c, (width - w) / 2, yh)

    signatures_table.drawOn(c, *coord(2.825, 26.25, cm))
    c.save()

    if os.path.exists(filename):
        with open(filename, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename("InformeCalificaciones.pdf")
            return response
