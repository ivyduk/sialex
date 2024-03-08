import logging
import csv

from administracion.models import Pago, ReciboPreinscripcion, PreinscripcionHorarioCurso, DescuentoAplicado

logging.basicConfig(filename='migration_logs',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger('sialex')

estado_recibo_mapper = {
    1: "CANCELADO", # Por eliminación en Preinscripción o Formalización. En liberacion de cupos
    2: "PENDIENTE", # Con pagos pendientes
    3: "PAGADO", # Sin saldo Pendiente
    4: "DEVUELTO" # Aplicación de proceso de devolución
}

estado_preinscripcion_mapper = {
    1: "INSCRITO",
    2: "APLAZADO_USUARIO",
    3: "PENDIENTE",
    4: "APLAZADO_DEP",
    5: "PREINSCRITO",
    6: "CANCELADO",
    7: "CANCELADO_FORMALIZACION"
}

headers = [
    'periodo', 'documento', 'preinscripcion_id', 'Estado', 'Requerido', 'Acumulado', 'Diferencia', 'Tarifa', 'Pagado', 'Diferencia',
    'Descuento', 'Descuento id', 'Beca', 'Saldo A Favor'
]


def main():
    queryset_recibo = ReciboPreinscripcion.objects.filter(migrado=False)
    recibos_cancelado = 0
    recibos_pendiente = 0
    recibos_pagado = 0
    recibos_devuelto = 0
    recibos_discrepancia_pendiente = 0
    recibos_discrepancia_inscrito = 0
    recibos_discrepancia_pagado = 0
    recibos_descuento_aplicado_no_encontrado = 0

    progreso = 0
    total = len(queryset_recibo.all())

    with open('discrepancias.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Headers

        for recibo in queryset_recibo:
            progreso += 1

            if progreso % 500 == 0:
                print(str(int((progreso * 100) / total)) +' % Completado')

            if recibo.estado_recibo == 1:
                recibos_cancelado += 1

            if recibo.estado_recibo == 2:
                recibos_pendiente += 1

            if recibo.estado_recibo == 3:
                recibos_pagado += 1

            if recibo.estado_recibo == 4:
                recibos_devuelto += 4

            logger.info('-- Recibo ' + str(recibo.id) + " Preinscripcion " + str(recibo.preinscripcion.id) + "-->" +
                        estado_preinscripcion_mapper.get(recibo.preinscripcion.estado_preinscripcion))
            descuento_id = None
            pagado_total = 0
            pagado_usuario = 0
            pagado_beca = 0
            pagado_descuento = 0
            pagado_saldo = 0
            fecha_pago = None
            preinscripcion_curso = PreinscripcionHorarioCurso.objects.filter(id=recibo.preinscripcion.id).first()
            if preinscripcion_curso and preinscripcion_curso.horario_cupo.curso.nivel.costo_materiales:
                valor_materiales = preinscripcion_curso.horario_cupo.curso.nivel.costo_materiales
                tarifa = preinscripcion_curso.horario_cupo.curso.oferta_academica.tarifa
            else:
                valor_materiales = 0
                tarifa = recibo.preinscripcion.valor_preinscripcion

            for pago in recibo.pagos.all():
                pagado_total += pago.financiero.valor
                if pago.tipo == 'Pago Usuario':
                    pagado_usuario += pago.financiero.valor
                    if not fecha_pago:
                        fecha_pago = pago.fecha_hora
                    elif fecha_pago < pago.fecha_hora:
                        fecha_pago = pago.fecha_hora
                elif pago.tipo == 'Beca':
                    pagado_beca += pago.financiero.valor
                elif pago.tipo == 'Descuento':
                    pagado_descuento += pago.financiero.valor
                    descuento_aplicado = DescuentoAplicado.objects.filter(id=pago.financiero.id).first()
                    if not descuento_aplicado:
                        logger.warning("Descuento Aplicado no encontrado Financiero id: " + str(pago.financiero.id))
                        recibos_descuento_aplicado_no_encontrado += 1
                    else:
                        descuento_id = descuento_aplicado.descuento_id
                elif pago.tipo == 'Saldo a favor':
                    pagado_saldo += pago.financiero.valor
                logger.info('--Pago--' + str(pago.financiero.valor) + '--Tipo--' + str(pago.tipo))

            recibo.valor_pagado = pagado_total
            recibo.valor_pagado_usuario = pagado_usuario
            recibo.valor_pagado_beca = pagado_beca
            recibo.valor_pagado_descuento = pagado_descuento
            recibo.valor_pagado_saldo = pagado_saldo
            recibo.descuento_id = descuento_id
            recibo.valor_materiales = valor_materiales
            recibo.fecha_pago = fecha_pago
            recibo.migrado = True
            recibo.save()

            #### Validaciones
            if recibo.estado_recibo != 1 and recibo.estado_recibo != 4:
                discrepancia = False
                if recibo.valor_requerido != recibo.valor_pagado:
                    logger.warning("Discrepancia total: requerido "+str(recibo.valor_requerido)+" acumulado "
                                   + str(recibo.valor_pagado))
                    discrepancia = True

                if (tarifa + valor_materiales) != recibo.valor_pagado_usuario:
                    logger.warning("Discrepancia pagado: tarifa + materiales " +
                                   str(tarifa + valor_materiales)
                                   + " Usuario " +
                                   str(recibo.valor_pagado_usuario + recibo.valor_pagado_beca +
                                       recibo.valor_pagado_saldo)
                                   )
                    discrepancia = True

                if discrepancia:
                    periodo = None
                    if preinscripcion_curso:
                        periodo = preinscripcion_curso.horario_cupo.curso.oferta_academica.periodo.alias

                    disc = [
                        periodo,
                        recibo.preinscrito.numero_documento,
                        recibo.preinscripcion.id,
                        estado_preinscripcion_mapper.get(recibo.preinscripcion.estado_preinscripcion),
                        recibo.valor_requerido,
                        recibo.valor_pagado,
                        recibo.valor_requerido - recibo.valor_pagado,
                        tarifa + valor_materiales,
                        recibo.valor_pagado_usuario,
                        (tarifa + valor_materiales) - (
                                recibo.valor_pagado_usuario+recibo.valor_pagado_beca+recibo.valor_pagado_beca
                        ),
                        pagado_descuento,
                        descuento_id if descuento_id else 0,
                        recibo.valor_pagado_beca,
                        recibo.valor_pagado_saldo
                    ]
                    writer.writerow(disc)
                    if recibo.estado_recibo == 2:
                        if recibo.preinscripcion.estado_preinscripcion == 3:
                            recibos_discrepancia_pendiente += 1
                        elif recibo.preinscripcion.estado_preinscripcion == 1:
                            recibos_discrepancia_inscrito += 1

    logger.info('--------------------------------------------------------------------')
    logger.info('Resumen Resultados')
    logger.info('- Total Recibos procesados: ' + str(total))
    logger.info('- Total Recibos cancelado: ' + str(recibos_cancelado))
    logger.info('- Total Recibos pendiente: ' + str(recibos_pendiente))
    logger.info('- Total Recibos pagado: ' + str(recibos_pagado))
    logger.info('- Total Recibos devuelto: ' + str(recibos_devuelto))
    logger.info('- Total Recibos pendiente + discrepancia: ' + str(recibos_discrepancia_pendiente))
    logger.info('- Total Recibos inscrito + discrepancia: ' + str(recibos_discrepancia_inscrito))
    logger.info('- Total Recibos pagado + discrepancia: ' + str(recibos_discrepancia_pagado))
    logger.info('- Total Recibos descuento aplicado no encontrado : ' + str(recibos_descuento_aplicado_no_encontrado))


if __name__ == '__main__':
    main()


