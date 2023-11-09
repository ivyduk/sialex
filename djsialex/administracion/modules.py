from .models import SaldoAFavor, Beca, DescuentoAplicado, DocumentosDescuentoSolicitado, Pago, ReservasSaldo


class AyudanteFinancieros(object):
    """Clase que realiza operaciones de consulta y actualización de financieros"""

    def __init__(self, persona, periodo):
        self.persona = persona
        self.periodo = periodo
        self.saldos = []
        self.beca = None
        self.descuento_aplicado = None
    
    def calcular_valor_preinscripcion_curso(self, tarifa_plena, nivel, descuento, valor_materiales):
        valor = tarifa_plena
        #Diccionario para mostrar en interfaz
        detallado = {}
        self._buscar_saldos_a_favor_disponibles()
        self._buscar_beca(nivel, 1)
        if self.beca:
            valor = valor - self.beca.valor
            detallado['beca'] = {}
            detallado['beca']['id'] = self.beca.id
            detallado['beca']["nombre"] = "Beca " + str(nivel.nombre) + self.beca.periodo_generado.alias
            detallado['beca']["signo"] = "-"
            valor_beca = (tarifa_plena * self.beca.tipo_beca.porcentaje) / 100
            detallado['beca']["valor"] = str(valor_beca)
            detallado['beca']["porcentaje"] = str(self.beca.tipo_beca.porcentaje)
            valor = valor - valor_beca
        if descuento:
            valor_descuento = (valor * descuento.porcentaje) / 100
            valor = valor - valor_descuento
            detallado['descuento'] = {}
            detallado['descuento']['id'] = descuento.id
            detallado['descuento']["nombre"] = descuento.nombre
            detallado['descuento']["signo"] = "-"
            detallado['descuento']["valor"] = str(valor_descuento)
            detallado['descuento']['porcentaje'] = str(descuento.porcentaje)
        if valor_materiales > 0:
            valor += valor_materiales
            detallado['materiales'] = valor_materiales
        if self.saldos:
            detallado['saldos'] = []
            for saldo in self.saldos:
                valor_saldo_disponible = saldo.valor
                reservas_saldo = saldo.reservassaldo_set.all()
                for reserva in reservas_saldo:
                    valor_saldo_disponible = saldo.valor - reserva.valor

                #valor_saldo_disponible = saldo.valor-saldo.valor_reservado
                valor = valor - valor_saldo_disponible
                saldo_dic = {}
                saldo_dic["id"] = saldo.id
                saldo_dic["nombre"] = "Saldo a favor- " + saldo.periodo_generado.alias
                saldo_dic["signo"] = "-"
                saldo_dic["valor"] = str(valor_saldo_disponible)
                if valor > 0:
                    saldo_dic["valor"] = str(valor_saldo_disponible)
                    resto_saldo = 0
                else:
                    resto_saldo = valor
                    saldo_dic["valor"] = str(valor + valor_saldo_disponible)
                    valor = 0
                if float(saldo_dic["valor"]) > 0:
                    detallado['saldos'].append(saldo_dic)
                if resto_saldo < 0:
                    break
        return valor, detallado

    # TODO - escribir metodo para examen

    def calcular_valor_preinscripcion_examen(self, tarifa_examen):
        valor = tarifa_examen
        #Diccionario para mostrar en interfaz
        detallado = {}
        self._buscar_saldos_a_favor_disponibles()

        if self.saldos:
            detallado['saldos'] = []
            for saldo in self.saldos:
                valor_saldo_disponible = saldo.valor
                reservas_saldo = saldo.reservassaldo_set.all()
                for reserva in reservas_saldo:
                    valor_saldo_disponible = saldo.valor - reserva.valor

                # valor_saldo_disponible = saldo.valor-saldo.valor_reservado
                valor = valor - valor_saldo_disponible
                saldo_dic = {}
                saldo_dic["id"] = saldo.id
                saldo_dic["nombre"] = "Saldo a favor- " + saldo.periodo_generado.alias
                saldo_dic["signo"] = "-"
                saldo_dic["valor"] = str(valor_saldo_disponible)
                if valor > 0:
                    saldo_dic["valor"] = str(valor_saldo_disponible)
                    resto_saldo = 0
                else:
                    resto_saldo = valor
                    saldo_dic["valor"] = str(valor + valor_saldo_disponible)
                    valor = 0
                if float(saldo_dic["valor"]) > 0:
                    detallado['saldos'].append(saldo_dic)
                if resto_saldo < 0:
                    break
        return valor, detallado

    def actualizar_financieros_creacion_recibo(self, recibo_preinscripcion, detallado):
        if "saldos" in detallado:
            for s in detallado['saldos']:
                try:
                    saldo = SaldoAFavor.objects.get(pk=s['id'])
                    reserva_saldo = ReservasSaldo(saldo=saldo, valor=float(s['valor']), preinscripcion_reserva=recibo_preinscripcion.preinscripcion)
                    reserva_saldo.save()
                except SaldoAFavor.DoesNotExist:
                    pass
        if "beca" in detallado:
            try:
                beca = Beca.objects.get(pk=detallado['beca']['id'])
                beca.estado_beca = 2
                beca.valor = detallado['beca']['valor']
                beca.save()
            except Beca.DoesNotExist:
                pass
        if "descuento" in detallado:
            try:
                descuento = DescuentoAplicado(
                    beneficiario=self.persona,
                    periodo_generado=self.periodo,
                    valor=detallado['descuento']['valor'],
                    descuento_id=detallado['descuento']['id'],
                    preinscripcion_generada=recibo_preinscripcion.preinscripcion
                )
                descuento.save()
                for doc in descuento.descuento.documentos_requeridos.filter(activo=True):
                    documento_descuento = DocumentosDescuentoSolicitado(
                        descuento_aplicado=descuento,
                        documento_requerido=doc
                    )
                    documento_descuento.save()
            except DescuentoAplicado.ValidationError:
                pass

    def actualizar_financieros_cancelacion_preinscripcion_sin_pago(self, preinscripcion, tipo_curso):
        self._buscar_saldos_a_favor_disponibles()
        self._buscar_beca(preinscripcion.horario_cupo.curso.nivel, 3)
        if self.beca:
            self.beca.valor = 0
            self.beca.estado_beca = 1
            self.beca.save()
        if self.saldos:
            for saldo in self.saldos:
                reservas_saldo = saldo.reservassaldo_set.all()
                for reserva in reservas_saldo:
                    if reserva.preinscripcion_reserva.id == preinscripcion.id:
                        reserva.valor = 0
                        reserva.save()
        if tipo_curso:
            self._buscar_descuento_aplicado(preinscripcion.descuento_solicitado, preinscripcion, 1)
            if self.descuento_aplicado:
                self.descuento_aplicado.estado_descuento = 3
                self.descuento_aplicado.save()

            self._buscar_beca(preinscripcion.horario_cupo.curso.nivel, 2)
            if self.beca:
                self.beca.valor = 0
                self.beca.estado_beca = 1
                self.beca.save()
            elif self._buscar_beca(preinscripcion.horario_cupo.curso.nivel, 3):
                self.beca.valor = 0
                self.beca.estado_beca = 1
                self.beca.save()

    def _buscar_saldos_a_favor_disponibles(self):
        self.saldos = SaldoAFavor.objects.filter(activo=True, periodo_generado__inicio__gte=self.periodo.inicio-4, beneficiario=self.persona).order_by('-valor')

    def _buscar_beca(self, nivel, estado):
        try:
            self.beca = Beca.objects.get(estado_beca=estado, beneficiario=self.persona, periodo_generado__inicio__gte=self.periodo.inicio-4, nivel_idioma=nivel)
        except Beca.DoesNotExist:
            self.beca = None
        return self.beca

    def _buscar_descuento_aplicado(self, descuento, preinscripcion, estado):
        try:
            self.descuento_aplicado = DescuentoAplicado.objects.get(estado_descuento=estado, preinscripcion_generada = preinscripcion, descuento = descuento)
        except DescuentoAplicado.DoesNotExist:
            self.descuento_aplicado = None


def check_saldo_cargado(recibo):
    saldo_flag = False
    saldo = SaldoAFavor.objects.filter(recibo_preinscripcion_generado=recibo, activo=True)
    if saldo:
        saldo_flag = True
    return saldo_flag


class CalcularPagosRecibo(object):
    """Clase que realiza calculo de pagos, pendiente y sobrante por recibo de preinscripción"""

    def __init__(self, recibopreinscripcion):
        self.recibo = recibopreinscripcion

    def calcular_pagos(self):
        pagos = Pago.objects.filter(recibo_preinscripcion=self.recibo)
        pagado = 0
        if pagos:
            for pago in pagos:
                pagado += pago.financiero.valor
        pendiente = self.recibo.valor_requerido - pagado
        sobrante = 0
        if pendiente < 0:
            sobrante = (-pendiente)
            pendiente = 0
        return pagado, sobrante, pendiente, pagos