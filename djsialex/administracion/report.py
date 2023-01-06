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
    ninios = d_matricula.grupo.horarioCurso.curso.oferta_academica.programa.para_ninios

    d_estudiante = d_matricula.estudiante
    d_calificaciones = report['calificaciones']

    nombre_estudiante = d_estudiante.primer_nombre + " " + d_estudiante.segundo_nombre + " " + d_estudiante.primer_apellido + " " + d_estudiante.segundo_apellido

    calificaciones = []
    for i in d_calificaciones:
        calificaciones.append(
            {"label": i.nota.nombre, "percentage": str(i.nota.ponderacion), "grade": str(i.calificacion)})

    filename = "/tmp/" + str(randrange(100)) + ".pdf"
    data = {
        "_sn": nombre_estudiante,
        "_lvl": d_grupo.nombre,
        "__grades": calificaciones,
        "__final": str(report['matricula'].calificacionFinal),
        "__abs": str(report['matricula'].total_fallas) + " de 12 horas permitidas",
        "__result": str(ESTADOS_ACADEMICOS_MATRICULA[d_matricula.estado_matricula - 1][1]),
        "__score1": "470-500",
        "__label1": "Excelente",
        "__score2": "400-469",
        "__label2": "Bueno",
        "__score3": "350-399",
        "__label3": "Aceptable",
        "__score4": "  0-349",
        "__label4": "Insuficiente",

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
    table_level_name = Paragraph('Nivel:', styleN)

    # StudentData
    value_student_name = Paragraph(data['_sn'], styleBH)
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

    # SummaryEquivalences
    table_summary_equivalencias_label = Paragraph('Equivalencias', styleBH)
    table_summary_score1 = Paragraph(data['__score1'], styleN)
    table_summary_score2 = Paragraph(data['__score2'], styleN)
    table_summary_score3 = Paragraph(data['__score3'], styleN)
    table_summary_score4 = Paragraph(data['__score4'], styleN)
    table_summary_value1 = Paragraph(data['__label1'], styleBH)
    table_summary_value2 = Paragraph(data['__label2'], styleBH)
    table_summary_value3 = Paragraph(data['__label3'], styleBH)
    table_summary_value4 = Paragraph(data['__label4'], styleBH)

    student_data = [
        [table_student_name, value_student_name],
        [table_level_name, value_level_name]]

    summary_data = [
        [table_summary_final, table_summary_grade],
        [table_summary_absenteeism_label, table_summary_absenteeism]
    ]

    equival_labl = [[table_summary_equivalencias_label]]
    equival_data = [[table_summary_score1, table_summary_value1],
                    [table_summary_score2, table_summary_value2],
                    [table_summary_score3, table_summary_value3],
                    [table_summary_score4, table_summary_value4]
                    ]

    records_data = [
        [table_record_description, table_record_percentage, table_record_final],
    ]
    for i in range(len(data['__grades'])):
        __g = data['__grades'][i]
        records_data.append([Paragraph(__g['label'], styleNull), Paragraph(__g['percentage'] + "%", styleNull),
                             Paragraph(__g['grade'], styleNull)])

    student_table = Table(student_data, colWidths=[3.5 * cm, 12.4 * cm])
    records_table = Table(records_data, colWidths=[4.0 * cm, 2 * cm, 2 * cm])
    summary_table = Table(summary_data, colWidths=[6.95 * cm, 6.95 * cm])
    equival_label = Table(equival_labl, colWidths=[4 * cm])
    equival_table = Table(equival_data, colWidths=[2 * cm, 2 * cm])
    
    if ninios == True:
        tabla_data = [
            [records_table, [equival_label, equival_table]],
        ]
    else:
        tabla_data = [
            [records_table],
        ]

    data_table = Table(tabla_data, colWidths=[10 * cm, 6 * cm])

    simple_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

    equival_label.setStyle(simple_style)
    equival_table.setStyle(simple_style)
    records_table.setStyle(simple_style)
    summary_table.setStyle(simple_style)
    data_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    student_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    c = canvas.Canvas(filename, pagesize=letter)

    c.drawImage(logo, document_width - print_width, document_height - print_height, width=print_width,
                height=print_height,
                mask='auto')
    c.setPageCompression(1)
    c.setAuthor("Universidad Nacional de Colombia")
    c.setTitle("Boletín de calificaciones")
    c.setAuthor("sialex framework")
    c.setProducer("sialex framework")
    c.setCreator("sialex framework")

    w, h = student_table.wrap(0, 0)
    yh = height - h - (5.5 * cm)
    yh_ = yh
    student_table.drawOn(c, (width - w) / 2, yh)

    w, h = data_table.wrap(0, 0)
    yh = yh - h - (0.5 * cm)
    data_table.drawOn(c, (width - w) / 2, yh)

    w, h = summary_table.wrap(0, 0)
    yh = yh - h - (0.5 * cm)
    summary_table.drawOn(c, (width - w) / 2, yh)

    c.save()

    if os.path.exists(filename):
        with open(filename, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename("InformeCalificaciones.pdf")
            return response