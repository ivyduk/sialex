from administracion.models import AutorizadoCurso, ReciboPreinscripcion, DescuentoAplicado, SaldoAFavor, Beca, \
    ReservasSaldo
from django.db import transaction

class AyudanteAnulacion(object):

    """Clase que realiza operaciones de consulta y actualización de recibos, descuentos,
     becas y autorizaciones
     """

    def __init__(self, persona, periodo, preinscripcion):
        self.persona = persona
        self.periodo = periodo
        self.preinscripcion = preinscripcion
        self.recibos = None
        self.becas = None
        self.descuentos = None
        self.autorizaciones = None
        self.saldos = None
        self.tieneAutorizacion = False

    def anulacionPreinscripcion(self):

        with transaction.atomic():
            self.autorizaciones = AutorizadoCurso.objects.filter(
                numero_documento=self.preinscripcion.persona.numero_documento,
                tipo_documento_id=self.preinscripcion.persona.tipo_documento,
                curso_autorizado_id=self.preinscripcion.horario_cupo.curso_id).all()

            self.recibos = ReciboPreinscripcion.objects.filter(preinscripcion_id=self.preinscripcion.id).all()
            self.descuentos = DescuentoAplicado.objects.filter(preinscripcion_generada_id=self.preinscripcion.id,
                                                      estado_descuento=1).all()  # estado: SELECCIONADO
            self.saldos = ReservasSaldo.objects.filter(preinscripcion_reserva=self.preinscripcion).all()
            #self.saldos = SaldoAFavor.objects.filter(preinscripcion_reserva=self.preinscripcion).all()
            self.becas = Beca.objects.filter(nivel_idioma=self.preinscripcion.horario_cupo.curso.nivel,
                                    estado_beca=1).all()  # estado: PENDIENTE

            if len(self.autorizaciones) > 0:
                self.tieneAutorizacion = True

            self.devolverAutorizacion()
            self.devolverSaldos()
            self.devolverBeca()

            self.anularRecibos()
            self.anularDescuentos()

    def anularRecibos(self):

        for recibo in self.recibos:
            recibo.estado_recibo = 1  # Cancelado
            recibo.save()

    def devolverBeca(self):

        for beca in self.becas:
            beca.estado_beca = 1  # Asignada
            beca.save()

    def anularDescuentos(self):

        for descuento in self.descuentos:
            descuento.estado_descuento = 4  # Anulado
            descuento.save()

    # Devolver autorización a estado original de Autorizado: Se asume que si una persona es autorizada a un curso y se preinscribe,
    # entonces el curso al que se preinscribió es el autorizado
    def devolverAutorizacion(self):

        for autorizacion in self.autorizaciones:
            autorizacion.estado = 1  # Autorizado
            autorizacion.save()

    def devolverSaldos(self):

        if self.saldos:
            for saldo in self.saldos:
                saldo.valor = 0
                saldo.save()