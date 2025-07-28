import uuid
import os
from auditlog.registry import auditlog


from django.db import models
from django.dispatch import receiver
from django.http import request
from django.db.models.signals import post_save, m2m_changed
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext_lazy as _



from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.cache import cache
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.utils.text import slugify

from ckeditor.fields import RichTextField


from administracion.enums import *

import logging
LOGGER = logging.getLogger(__name__)


class DatosEstudiantesModel(models.Model):
    id                      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_sub_proyecto_curso   = models.CharField(max_length=15)
    tipo_documento          = models.IntegerField()
    numero_documento        = models.CharField(max_length=100)
    primer_nombre           = models.CharField(max_length=100)
    segundo_nombre          = models.CharField(max_length=100)
    primer_apellido         = models.CharField(max_length=100)
    segundo_apellido        = models.CharField(max_length=100)
    sexo_biologico          = models.IntegerField()
    estado_civil            = models.CharField(max_length=3)
    fecha_nacimiento        = models.DateField()
    pais_nacimiento         = models.IntegerField()
    departamento_nacimiento = models.IntegerField()
    ciudad_nacimiento       = models.IntegerField()
    nivel_formacion         = models.IntegerField()
    egresado_un             = models.IntegerField()
    vinculacion             = models.IntegerField()
    telefono_fijo           = models.CharField(max_length=15)
    ext                     = models.CharField(max_length=3)
    celular                 = models.CharField(max_length=15)
    email                   = models.CharField(max_length=254)
    direccion_residencia    = models.CharField(max_length=1000)
    pais_residencia         = models.IntegerField(),
    departamento_residencia = models.IntegerField()
    ciudad_residencia       = models.IntegerField()
    descuento               = models.IntegerField()
    valor_inscripcion       = models.FloatField(null=False)
    valor_pago              = models.FloatField(null=False)
    fecha_pago              = models.DateField()
    no_soporte_de_pago      = models.CharField(max_length=100)
    tipo_pago               = models.IntegerField()
    tarifa_materiales       = models.FloatField(null=False)


class Pais(models.Model):

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    alias = models.CharField(max_length=5)
    indicativo = models.IntegerField(default=0)
    hermes_id = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre + " - " + self.alias

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Paises"

    def getIndicativo(self, alias):
        return Pais.objects.get(alias=alias).indicativo


class Region(models.Model):
    def __str__(self):
        return self.nombre

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    hermes_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"


class Ciudad(models.Model):
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    hermes_id = models.IntegerField(default=0)


class Idioma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, help_text='Nombre Idioma')
    alias = models.CharField(max_length=5, help_text='Alias para identificar facilmente el idioma')

    class Meta:
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas"
        ordering = ["nombre"]

    def get_absolute_url(self):
        """
         Devuelve la url para acceder a una instancia particular de Idioma.
         """
        return reverse('idioma-detail', args=[str(self.id)])

    def __str__(self):
        """
		Cadena para representar el modelo Idioma
		:return: alias
		"""
        return self.nombre.upper()


class DocumentoRequerido(models.Model):
    """
    	Modelo que representa un Documento requerido para un descuento
    	durante la formalización de la inscripción
    """

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=250, help_text='Nombre del documento Requerido')
    activo = models.BooleanField(default=False, help_text='Determina si es un documento solicitado actualmente')
    unica_entrega = models.BooleanField(default=False, help_text='Determina si el documento se solicita por una única vez en la vida al estudiante')

    class Meta:
        verbose_name = "Documento requerido"
        verbose_name_plural = "Documentos requeridos"

    def __str__(self):
        """
    	Cadena para representar el modelo Horario
    	:return: nombre
    	"""
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Documento Requerido.
        """
        return reverse('documento-requerido-detail', args=[str(self.id)])


class ContenidoNivel(models.Model):

    id = models.AutoField(primary_key=True, editable=False)
    alias = models.CharField(max_length=200, help_text='Alias para identificar el contenido fácilmente')
    version_actual = models.IntegerField(default=0, help_text='Esta versión se incrementa al subir un documento')

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Contenido de Nivel.
        """
        return reverse('contenido-nivel-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Nivel
        :return: alias
        """
        return self.alias

    class Meta:
        verbose_name = "Contenido nivel"
        verbose_name_plural = "Contenido niveles"


class ContenidoNivelVersion(models.Model):

    def get_upload_path(instance, filename):
        return os.path.join('upload/public/content-level/', now().date().strftime("%Y/%m/%d"),
                            str(uuid.uuid1()) + ".pdf")

    id = models.AutoField(primary_key=True, editable=False)
    alias = models.CharField(max_length=200, help_text='Alias para identificar la versión del documento fácilmente')
    version = models.IntegerField(default=1, help_text='Versión actual del documento')
    contenido_nivel = models.ForeignKey(ContenidoNivel, on_delete=models.CASCADE)
    documento = models.FileField(blank=True,null=True,upload_to=get_upload_path, help_text='archivo a subir')  # MEDIA_ROOT/documents/
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Contenido de Nivel.
        """
        return reverse('contenido-nivel-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Nivel
        :return: alias
        """
        return self.alias

    class Meta:
        verbose_name = "Contenido nivel"
        verbose_name_plural = "Contenido niveles"
        ordering = ['-version']


class Nivel(models.Model):
    """
		Modelo que representa el nivel de un idioma como A1, B2, B3, etc.

	"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.IntegerField(default=1, help_text='Indica el orden del nivel')
    idioma = models.ForeignKey(Idioma, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, help_text='Nombre del nivel')
    alias = models.CharField(max_length=20, help_text='Alias para identificar el nivel fácilmente')
    predecesor = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, help_text='Nivel anterior para periodos regulares')
    contenido = models.OneToOneField(ContenidoNivel, on_delete=models.CASCADE, null=False, editable=False)
    intensidad_horaria = models.IntegerField(default=1, validators=[
            MinValueValidator(0)
        ], verbose_name="intensidad horaria (horas)", help_text='Indica número de horas totales del nivel')
    fallas_maximas = models.IntegerField(default=1, validators=[
            MinValueValidator(0)
        ], help_text='Número de horas que durará la enseñanza del nivel')
    activo = models.BooleanField(default=True, help_text='Determina si es un nivel está disponible actualmente')
    costo_materiales = models.FloatField(help_text='Valor de materiales', verbose_name="Valor Materiales (COP)", default=0)
    edad_minima = models.IntegerField(default=1, help_text='Edad mínima permitida', null=True)
    edad_maxima = models.IntegerField(default=100, help_text='Edad máxima permitida', null=True)
    documentos_pago = models.CharField(max_length=300, default='Recibo Original y copia')
    mensaje_formalizacion = RichTextField(blank=True, null=True, verbose_name="Instrucciones Formalización")

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Nivel.
        """
        return reverse('nivel-detail', args=[str(self.id)])

    class Meta:
        verbose_name = "Nivel"
        verbose_name_plural = "Niveles"
        ordering = ["orden", "nombre"]


    def __str__(self):
        """
		Cadena para representar el modelo Nivel
		:return: alias
		"""
        return self.alias

    def getNombreNivelIdioma(self):

        idioma_nombre = ''
        if self.idioma:
            idioma_nombre = self.idioma.nombre
        return idioma_nombre + '-' + self.nombre

    @staticmethod
    def getNivelesProgramasActivos(idioma_id):
        return Nivel.objects.filter(
            idioma_id=idioma_id,
            programaacademico__activo=True,
            programaacademico__ofertaacademica__periodo__activo=True,
            programaacademico__ofertaacademica__periodo__finalizado=False,
            activo=True
        ).order_by('orden')

    def save(self, *args, **kwargs):
        if self.mensaje_formalizacion == '':
            self.mensaje_formalizacion = None
        super(Nivel, self).save(*args, **kwargs)


class EPS(models.Model):
    """
       Modelo que representa una EPS
    """
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=100, help_text='Nombre de EPS')

    def __str__(self):
        """
        Cadena para representar el modelo EPS
        :return: nombre
        """
        return self.nombre


class EscalaNota(models.Model):
    """
	Modelo que representa la escala de notas de un programa academico
	"""
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=100, help_text='Nombre para la escala de notas a utilizar en los programas académicos ', unique=True)
    nota_minima = models.FloatField(default=0.0, help_text='Nota mínima de la escala')
    nota_maxima = models.FloatField(default=5.0, help_text='Nota máxmio de la escala')
    nota_aprobatoria = models.FloatField(default=3.0, help_text='Nota con la que se aprobaría el curso')
    numero_decimales = models.IntegerField(default=2, help_text='Número de decimales para manejo de cálculos')

    class Meta:
        verbose_name = "Escala"
        verbose_name_plural = "Escalas de Notas"

    def __str__(self):
        """
		Cadena para representar el modelo Periodicidad
		:return: nombre
		"""
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Escala nota.
        """
        return reverse('escala-nota-detail', args=[str(self.id)])


class Periodicidad(models.Model):
    """
	Modelo que representa la periodicidad de un periodo como semestral,
	bimestral, otro
	"""

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    meses = models.IntegerField(help_text='Duración en meses de la periodicidad')

    class Meta:
        verbose_name = "Periodicidad"
        verbose_name_plural = "Periodicidades"

    def __str__(self):
        """
		Cadena para representar el modelo Periodicidad
		:return: nombre
		"""
        return self.nombre

    def get_absolute_url(self):
        """
         Devuelve la url para acceder a una instancia particular de Periodo.
         """
        return reverse('periodicidad-detail', args=[str(self.id)])


class Periodo(models.Model):
    """
	Modelo que representa un periodo en el cual se va a habilitar los procesos
	de inscripción y desarrollo de cursos y exámenes
	"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    abierto = models.BooleanField(default=True, verbose_name="Regular",
                                  help_text="Periodos abiertos al público, de periodicidad bimestral y semestral únicamente")
    periodo_anterior = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, help_text="En Periodos Regulares es obligatorio el antecesor para validar el proceso en los estudiantes")
    periodicidad = models.ForeignKey(Periodicidad, on_delete=models.CASCADE, help_text="Selecciona la duración académica del período")
    anio = models.IntegerField(verbose_name="año", help_text="Ingrese un año entre 2019 y 2050")
    secuencia = models.IntegerField(help_text="Semestral: 1-2, Bimestral: 1-4", blank=True)
    alias = models.CharField(max_length=20, unique=True, help_text="Se puede autogenerar o editar manualmente")
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del período")
    activo = models.BooleanField(default=False, help_text="Determina si se pueden crear elementos en el periodo")
    finalizado = models.BooleanField(default=False, help_text="Determina si el periodo ya no será visible para los usuarios al autenticarse")
    inicio = models.IntegerField(editable=False, null=True)
    fin = models.IntegerField(editable=False, null=True)
    fecha_inicio = models.DateField(default=timezone.now, help_text="Fecha Inicio del periodo")
    fecha_final = models.DateField(default=timezone.now, help_text="Fecha Final del periodo")
    fecha_pendientes = models.DateField(default=timezone.now, help_text="Fecha Para envio de pendientes")
    fecha_calificacion = models.DateField(default=timezone.now, help_text="Fecha Calificacion del periodo")

    class Meta:
        verbose_name = "Periodo"
        verbose_name_plural = "Periodos"
        ordering = ["anio", "alias"]

    def get_absolute_url(self):
        """
         Devuelve la url para acceder a una instancia particular de Periodo.
         """
        return reverse('periodo-detail', args=[str(self.id)])

    def __str__(self):
        """
		Cadena para representar el modelo Periodo
		:return: alias
		"""

        return self.nombre

    def save(self, *args, **kwargs):
            self.inicio = self.periodo_anterior.fin
            self.fin = self.inicio + self.periodicidad.meses
            super(Periodo, self).save(*args, **kwargs)

    def nombreAmigable(self):
        return str(self.anio) + " " + self.periodicidad.nombre + " - " + str(self.secuencia)


class ProgramaAcademico(models.Model):
    """
	Modelo que representa un programa academico en el cual se incluyen una serie de cursos y exámenes
	distribuidos por niveles
	"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50)
    idioma = models.ForeignKey(Idioma, on_delete=models.PROTECT)
    escala_nota = models.ForeignKey(EscalaNota, on_delete=models.PROTECT)
    edad_minima = models.IntegerField(default=1, help_text='Edad mínima permitida')
    edad_maxima = models.IntegerField(default=1, help_text='Edad máxima permitida')
    nivel = models.ManyToManyField(Nivel, help_text="Seleccione nivel para el Programa Academico")
    activo = models.BooleanField(default=False, help_text='Determina disponibilidad del programa académico')
    para_ninios = models.BooleanField(default=False, help_text='Determina si es para niños')
    descuento_obligatorio = models.BooleanField(
        default=False,
        help_text='Determina si se requiere selección de descuento obligatorio'
    )

    class Meta:
        verbose_name = "Programa Academico"
        verbose_name_plural = "Programas"
        ordering = ["nombre", "idioma"]

    def get_absolute_url(self):
        """
         Devuelve la url para acceder a una instancia particular de Programa Academico.
         """
        return reverse('programa-detail', args=[str(self.id)])

    def __str__(self):
        """
		Cadena para representar el modelo Programa Academico
		:return: alias
		"""
        return self.nombre


class Franja(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=50, default='franja', editable=False, unique=True)
    dia = models.IntegerField(
        choices=DIAS,
        unique=False,
        default=1
    )
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()

    def save(self, *args, **kwargs):
        self.nombre = str(self.get_dia_display()) + '-' + str(self.hora_inicio)[0:5] + '-' + str(self.hora_final)[0:5]
        super(Franja, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Franja"
        verbose_name_plural = "Franjas"

    def __str__(self):
        """
    	Cadena para representar el modelo Franja
    	:return: alias
    	"""
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Franja.
        """
        return reverse('franja-detail', args=[str(self.id)])


class Horario(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    alias = models.CharField(max_length=30, default='alias-horario')
    nombre = models.CharField(max_length=30, default='horario', editable=False, unique=True)
    franja = models.ManyToManyField(Franja, help_text="Seleccione las franjas que pertenecen al horario")

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"

    def __str__(self):
        """
    	Cadena para representar el modelo Horario
    	:return: nombre
    	"""
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Horario.
        """
        return reverse('horario-detail', args=[str(self.id)])


class Descuento(models.Model):
    """
	Modelo que representa un Descuento
	"""

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(max_length=200)
    porcentaje = models.FloatField(help_text='Porcentaje de descuento sobre la tarifa plena')
    documentos_requeridos = models.ManyToManyField(DocumentoRequerido, help_text="Seleccione")
    activo = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def __str__(self):
        """
        Cadena para representar el modelo Descuento
        :return: nombre
        """
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Descuento.
        """
        return reverse('descuento-detail', args=[str(self.id)])


class ConjuntoNotas(models.Model):
    """
    Modelo que representa un conjunto de notas
    """

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=150, default='conjunto_notas')

    class Meta:
        verbose_name = "Conjunto de notas"
        verbose_name_plural = "Conjuntos de notas"

    def __str__(self):
        """
        Cadena para representar el modelo Conjunto de Notas
        :return: nombre
        """
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Conjunto de Notas.
        """
        return reverse('conjunto_notas-detail', args=[str(self.id)])


class OfertaAcademica(models.Model):
    """
    Modelo que representa una oferta academica
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, editable=False, default="Oferta", help_text='Nombre para la oferta académica')
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, help_text='Selección de periodo')
    programa = models.ForeignKey(ProgramaAcademico, on_delete=models.PROTECT, help_text='Selección de programa académico')
    tarifa = models.FloatField(help_text='Valor neto para inscripción', verbose_name="Tarifa (COP)")
    descuentos = models.ManyToManyField(Descuento,blank=True)

    class Meta:
        verbose_name = "Oferta académica"
        verbose_name_plural = "Ofertas académicas"

    def save(self, *args, **kwargs):
        self.nombre = str(self.periodo.alias) + '-' + str(self.programa.nombre)
        super(OfertaAcademica, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Oferta Academica.
        """
        return reverse('oferta-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Oferta Academica
        :return: nombre
        """
        return self.nombre


class Curso(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre           = models.CharField(max_length=150, editable=False, default="curso", unique=True)
    #codigo_proyecto  = models.CharField(max_length=15,  editable=True, default="codigo", unique=True) esta en horario curso
    oferta_academica = models.ForeignKey(OfertaAcademica, on_delete=models.PROTECT)
    nivel            = models.ForeignKey(Nivel, on_delete=models.PROTECT)
    conjunto_notas   = models.ForeignKey(ConjuntoNotas, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def save(self, *args, **kwargs):
        self.nombre = str(self.oferta_academica.nombre) + '-' + str(self.nivel.nombre)
        super(Curso, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Curso.
        """
        return reverse('curso-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Curso
        :return: nombre
        """
        return self.nombre


class HorarioCurso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(editable=False, max_length=400, default="horario Cupo", unique=True)
    horario = models.ForeignKey(Horario, related_name='horarios', on_delete=models.PROTECT, help_text='Selección de horario')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    cupo_disponible = models.IntegerField()
    cupo_inicial = models.IntegerField(help_text='Cupo a ofertarse para público en general')
    cupo_autorizados = models.IntegerField(default=0)
    cupo_disponible_autorizados = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.nombre = str(self.horario.nombre) + '-' + str(self.curso.nombre)
        super(HorarioCurso, self).save(*args, **kwargs)

    def __str__(self):
        """
        Cadena para representar el modelo HorarioCurso
        :return: nombre
        """
        return self.nombre


class NotaParcial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conjunto_notas = models.ForeignKey(ConjuntoNotas, on_delete=models.PROTECT, null=True)
    nombre = models.CharField(max_length=200, help_text='Nombre de la nota a evaluar')
    tipo_nota = models.IntegerField(choices=TIPOS_NOTA, null=False, default=1, help_text='Tipo de la nota de acuerdo a profesor, Especializada o General')
    descripcion = models.TextField()
    ponderacion = models.IntegerField(verbose_name='Ponderación (%)')
    orden_nota_conjunto = models.IntegerField(verbose_name='Orden calificación', validators=[MinValueValidator(0)], help_text='debe ser orden entre 1 y el número de notas', default=1)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self):
        """
        Cadena para representar el modelo Nota parcial
        :return: nombre
        """
        return self.nombre + '-' + str(self.ponderacion) + '%'


class TipoDocumentoIdentidad(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"

    def __str__(self):
        """
    	Cadena para representar el modelo Tipo de Documento
    	:return: nombre
    	"""
        return self.nombre


class Discapacidad(models.Model):
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Discapacidad"
        verbose_name_plural = "Discapacidades"

    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)


class Profile(models.Model):
    # Para el registro se permiten campos nulos, en la activación se validan los demás campos
    # en un forms.py especifico para el perfil del usuario
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_documento = models.ForeignKey(TipoDocumentoIdentidad, on_delete=models.CASCADE, null=True)
    numero_documento = models.CharField(max_length=100, null=False, unique=True)

    primer_nombre = models.CharField(max_length=100, null=False)
    segundo_nombre = models.CharField(max_length=100, null=True, default="")
    primer_apellido = models.CharField(max_length=100, null=False)
    segundo_apellido = models.CharField(max_length=100, null=True, default="")

    ciudad_expedicion_documento = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=False,
                                                    related_name='profile_ciudad_expedicion_documento', default=107)
    genero_sexual = models.IntegerField(verbose_name='Sexo biológico',  choices=GENERO_SEXUAL, null=False, default=2)

    fecha_nacimiento = models.DateField(null=True, blank=False)
    ciudad_nacimiento = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=False,
                                          related_name='profile_ciudad_nacimiento', default=107)

    ciudad_residencia = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=False,
                                          related_name='profile_ciudad_residencia', default=107)
    direccion_residencia = models.CharField(
        max_length=1000,
        null=False,
    )

    direccion_sin_formato = models.CharField(
        max_length=1000,
        null=False,
    )

    indicativo_fijo = models.CharField(max_length=3, blank=True)
    telefono_fijo = models.CharField(max_length=15, blank=True)
    indicativo_celular = models.CharField(max_length=3, blank=True)
    telefono_celular = models.CharField(max_length=15, null=False, default='')
    tipo_sangre = models.IntegerField(choices=TIPOS_SANGRE, null=False, default=1)

    eps = models.ForeignKey(EPS, on_delete=models.CASCADE, null=True)

    email_confirmed = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)
    profile_active = models.BooleanField(default=False)
    cuenta_duplicada = models.BooleanField(default=False)
    cuenta_duplicada_desactivada = models.BooleanField(default=False)
    acepta_habeas_data = models.BooleanField(default=False)
    documento_identificacion_entregado = models.BooleanField(default=False)
    es_egresado = models.BooleanField(default=False)
    tipo_vinculacion_un = models.IntegerField(choices=TIPOS_VINCULACION, null=False, default=7) #Ninguna
    nivel_formacion = models.IntegerField(choices=NIVEL_FORMACION, null=False, default=1) #No Aplica
    estado_civil = models.IntegerField(choices=ESTADO_CIVIL, null=False, default=7) #Ninguna
    discapacidad = models.ForeignKey(Discapacidad, on_delete=models.CASCADE, null=True,
                                          related_name='profile_discapacidad', default=None)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['-id']

    @property
    def es_menor_de_edad(self):
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year - \
               ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad < 18
    
    @property
    def edad(self):
        hoy = date.today()
        diferencia = relativedelta(hoy, self.fecha_nacimiento)
        anios = diferencia.years
        meses = diferencia.months

        # Pluralidad
        anios_str = f'{anios} año{"s" if anios != 1 else ""}'
        meses_str = f'{meses} mes{"es" if meses != 1 else ""}'

        # Construir la cadena basada en el valor de las variables
        if anios == 0:
            return meses_str
        elif meses == 0:
            return anios_str
        else:
            return f'{anios_str} y {meses_str}'

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Profile.
        """
        return reverse('persona-detail', args=[str(self.id)])

    def getDocNombre(self):
        return self.numero_documento + '-' + self.primer_nombre

    def getNombres(self):
        segundo_nombre = ''
        if self.segundo_nombre:
            segundo_nombre = self.segundo_nombre
        return self.primer_nombre + ' ' + segundo_nombre

    def getApellidos(self):
        segundo_apellido = ''
        if self.segundo_apellido:
            segundo_apellido = self.segundo_apellido
        return self.primer_apellido + ' ' + segundo_apellido

    def getNombreCompleto(self):
        return self.getNombres() + ' ' + self.getApellidos()

    def getFechaNacimiento(self):
        DATE_FORMAT = "%d-%m-%Y"
        return self.fecha_nacimiento.strftime("%s" % (DATE_FORMAT))

    def getTelefonoFijo(self):
        indicativo = Pais.objects.get(alias=self.indicativo_fijo).indicativo
        return '(' + str(indicativo) + ') ' + self.telefono_fijo

    def getTelefonoCelular(self):
        indicativo = Pais.objects.get(alias=self.indicativo_celular).indicativo
        return '(' + str(indicativo) + ') ' + self.telefono_celular

    def __str__(self):
        """
    	Cadena para representar el modelo Profile
    	:return: nombre
    	"""
        return self.usuario.username + ' ' + self.primer_nombre + ' ' + self.primer_apellido

    def save(self, *args, **kwargs):
        self.direccion_residencia = self.direccion_sin_formato.replace('|', ' ')
        super(Profile, self).save(*args, **kwargs)


class PersonaContacto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombres = models.CharField(max_length=100, null=False)
    apellidos = models.CharField(max_length=100, null=False)
    numero_celular = models.CharField(max_length=20, null=False)
    correo_electronico = models.CharField(max_length=100, null=False)
    parentesco = models.IntegerField(choices=PARENTESCO, null=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(usuario=instance)
    instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.numero_documento = instance.username
    instance.profile.save()

@receiver(m2m_changed, sender=User.groups.through)
def user_group_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action == "pre_add":
        if 3 in pk_set: #3: Docente
            try:
                docente = Docente.objects.filter(persona=instance.profile)
            except:
                docente = None
            if not docente:
                docente = Docente(persona=instance.profile)
                docente.save()

#Revisar
class DocumentoIdentidad(models.Model):
    # Se debe usar para históricos
    id = models.AutoField(primary_key=True, editable=False)
    tipo = models.ForeignKey(TipoDocumentoIdentidad, on_delete=models.CASCADE)
    numero = models.CharField(max_length=100, unique=True)
    persona = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vigente = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"


class TipoDocente(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    tipo = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tipo


class Docente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.OneToOneField(Profile, on_delete=models.CASCADE)
    tipo_docente = models.ManyToManyField(TipoDocente)
    activo = models.BooleanField(default=True)

    def __str__(self):
        """
    	Cadena para representar el modelo Docente
    	:return: nombre
    	"""
        segundo_nombre = ''
        segundo_apellido = ''
        if self.persona.segundo_nombre:
            segundo_nombre = self.persona.segundo_nombre

        if self.persona.segundo_apellido:
            segundo_apellido = self.persona.segundo_apellido

        return self.persona.numero_documento + ' - ' + self.persona.primer_nombre + ' ' + segundo_nombre  + ' ' + self.persona.primer_apellido + ' ' + segundo_apellido


class Edificio(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=600)

    def __str__(self):
        """
        Cadena para representar el modelo Salon
        :return: nombre
        """
        return self.nombre


class Salon(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=600)
    edificio = models.ForeignKey(Edificio, on_delete=models.PROTECT)

    def __str__(self):
        """
    	Cadena para representar el modelo Salon
    	:return: nombre
    	"""
        return self.nombre

    class Meta:
        verbose_name = "Salon"
        verbose_name_plural = "Salones"


class GrupoAcademico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=500)
    codigo_proyecto = models.CharField(max_length=15, unique=True, null=True, blank=True) #AGREGADO
    horarioCurso = models.ForeignKey(HorarioCurso, on_delete=models.PROTECT)
    salones = models.ManyToManyField(Salon)
    codigo = models.IntegerField(default=9001)
    observaciones = models.TextField(max_length=1000, null=True)
    contenido_nivel_version = models.ForeignKey(ContenidoNivelVersion, on_delete=models.PROTECT, null=True)
    estado = models.IntegerField(choices=ESTADOS_GRUPO_ACADEMICO, default=0)
    fecha_inicio = models.DateField(default=timezone.now, null=True)
    fecha_final = models.DateField(default=timezone.now, null=True)
    enlace_virtual = models.URLField(max_length=255, null=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            ultimo_codigo = GrupoAcademico.objects.all().aggregate(largest=models.Max('codigo'))['largest']
            if ultimo_codigo is not None:
                self.codigo =  ultimo_codigo + 1

        super(GrupoAcademico, self).save(*args, **kwargs)

    def __str__(self):
        """
    	Cadena para representar el modelo GrupoAcademico
    	:return: nombre
    	"""
        return self.nombre


class Preinscripcion(models.Model):
    persona = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    estado_preinscripcion = models.IntegerField(choices=ESTADOS_ADMINISTRATIVOS_PREINSCRIPCION, default=5)
    fecha_preinscripcion = models.DateTimeField(auto_now_add=True)
    valor_preinscripcion = models.FloatField(default=0)
    codigo_hash = models.CharField(max_length=100, default='')
    requiere_facturacion = models.BooleanField(
        default=True,
        help_text='Determina si esta preinscripción requiere facturación electrónica'
    )
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        """
    	Cadena para representar el modelo Presinscripcion
    	"""
        return str(self.id) + "-" + self.persona.numero_documento


class PreinscripcionHorarioCurso(Preinscripcion):
    horario_cupo = models.ForeignKey(HorarioCurso, on_delete=models.CASCADE, null=True)
    descuento_solicitado = models.ForeignKey(Descuento, on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de preinscripcion.
        """
        return reverse('preinscripcion-detail', args=[str(self.id)])


class Matricula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudiante = models.ForeignKey(Profile, on_delete=models.PROTECT)
    grupo = models.ForeignKey(GrupoAcademico, on_delete=models.PROTECT)
    calificacionFinal = models.FloatField(default=0.0)
    total_fallas = models.IntegerField(default=0)
    estado_matricula = models.IntegerField(choices=ESTADOS_ACADEMICOS_MATRICULA, default=1)
    preinscripcion_generada = models.ForeignKey(Preinscripcion, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        """
    	Cadena para representar el modelo Matricula
    	:return: nombre
    	"""
        return self.estudiante.numero_documento + '-' + self.estudiante.primer_nombre + '-' + self.estudiante.primer_apellido

    @property
    def periodo(self):
        return self.preinscripcion_generada.horario_cupo.curso.oferta_academica.periodo if self.preinscripcion_generada else None


class Observacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    observacion = models.TextField(max_length=1000)
    matricula = models.ForeignKey(Matricula, on_delete=models.PROTECT)
    persona_asignadora = models.ForeignKey(Profile, on_delete=models.PROTECT)
    fecha_actualizacion = models.DateTimeField()
    cohorte = models.IntegerField(choices=COHORTE, default=1)


class FallaAsistencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricula = models.ForeignKey(Matricula, on_delete=models.PROTECT)
    persona_asignadora = models.ForeignKey(Profile, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)
    cantidad_fallas = models.IntegerField(default=0, validators=[MinValueValidator(0)])


class Calificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricula = models.ForeignKey(Matricula, on_delete=models.PROTECT)
    nota = models.ForeignKey(NotaParcial, on_delete=models.PROTECT)
    calificacion = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])


class DocentesGrupoAcademico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT)
    grupo_academico = models.ForeignKey(GrupoAcademico, on_delete=models.PROTECT)
    tipo_docente = models.ForeignKey(TipoDocente, on_delete=models.PROTECT)


class ExamenClasificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    idioma = models.ForeignKey(Idioma, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=200)
    cupo_inicial = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cupo_disponible = models.IntegerField(default=0)
    cupo_autorizado = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cupo_disponible_autorizado = models.IntegerField(default=0)
    tarifa = models.FloatField(verbose_name='Tarifa (COP)')
    edad_minima = models.IntegerField(default=17)
    docentes_evaluadores = models.ManyToManyField(Docente)
    lugar_aplicacion = models.CharField(max_length=300, default='')
    fecha_hora = models.DateTimeField(null=True)
    codigo_proyecto = models.IntegerField(null=True, blank=True)
    fecha_hora_recepcion_documentos = models.TextField(max_length=3000, default='')
    mensaje_formalizacion = RichTextField(blank=True, null=True, verbose_name="Instrucciones Formalización")

    def __str__(self):
        """
    	Cadena para representar el modelo Examen de Clasificacion
    	:return: nombre
    	"""
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Examen de Clasificacion.
        """
        return reverse('examen-clasificacion-detail', args=[str(self.id)])

    class Meta:
        verbose_name = "Examen de clasificación"
        verbose_name_plural = "Exámenes de clasificación"

    def getFechaAplicacion(self):
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M"

        return self.fecha_hora.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))

    def save(self, *args, **kwargs):
        if self.mensaje_formalizacion == '':
            self.mensaje_formalizacion = None
        super(ExamenClasificacion, self).save(*args, **kwargs)


class PreinscripcionExamen(Preinscripcion):
    examen = models.ForeignKey(ExamenClasificacion, on_delete=models.CASCADE, null=True)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de preinscripcion.
        """
        return reverse('preinscripcion-examen-detail', args=[str(self.id)])


class Autorizado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_documento = models.ForeignKey(TipoDocumentoIdentidad, on_delete=models.CASCADE, null=False)
    numero_documento = models.CharField(max_length=100, null=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=False);
    motivo = models.TextField()
    autorizado_por = models.ForeignKey(Profile, on_delete=models.CASCADE, null=False)
    fecha_hora_autorizacion = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(
        choices=ESTADOS_AUTORIZADO,
        unique=False,
        default=1)

    class Meta:
        ordering = ['-id']

    def getFechaAutorizacion(self):
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

        return self.fecha_hora_autorizacion.strftime(DATE_FORMAT)

class AutorizadoCurso(Autorizado):
    curso_autorizado = models.ForeignKey(Curso, related_name='autorizado_curso',on_delete=models.CASCADE, null=True)
    horario_curso_autorizado = models.ForeignKey(HorarioCurso, on_delete=models.CASCADE, null=True)

class AutorizadoExamen(Autorizado):
    examen = models.ForeignKey(ExamenClasificacion, on_delete=models.CASCADE, null=True)

class Financiero(models.Model):

    beneficiario = models.ForeignKey(Profile, on_delete=models.CASCADE)
    periodo_generado = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=False)
    valor = models.FloatField(null=False)

class DescuentoAplicado(Financiero):

    descuento = models.ForeignKey(Descuento, on_delete=models.CASCADE, null=False)
    estado_descuento = models.IntegerField(choices=ESTADOS_DESCUENTO, default=1)
    preinscripcion_generada = models.ForeignKey(Preinscripcion, on_delete=models.DO_NOTHING, null=True)


class DocumentosDescuentoSolicitado(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    descuento_aplicado = models.ForeignKey(DescuentoAplicado, on_delete=models.CASCADE, null=False)
    documento_requerido = models.ForeignKey(DocumentoRequerido, on_delete=models.CASCADE, null=False)
    entregado = models.BooleanField(default=False)


class TipoBeca(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    porcentaje = models.FloatField()

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Tipo de beca.
        """
        return reverse('tipo-beca-detail', args=[str(self.id)])


class Beca(Financiero):

    tipo_beca = models.ForeignKey(TipoBeca, on_delete=models.CASCADE, null=False)
    asignada_por = models.ForeignKey(Profile, on_delete=models.CASCADE, null=False, related_name="asignador")
    nivel_idioma = models.ManyToManyField(Nivel, verbose_name=("NivelesBeca"))
    fecha_asignacion = models.DateTimeField()
    estado_beca = models.IntegerField(choices=ESTADOS_BECA, default=1)

    class Meta:
        ordering = ['-id']


class ComprobanteBanco(Financiero):

    numero_recibo = models.CharField(max_length=100, null=False)
    tipo_comprobante = models.IntegerField(choices=TIPOS_COMPROBANTE, default=1)
    preinscripcion_generada = models.ForeignKey(Preinscripcion, on_delete=models.DO_NOTHING, null=False)
    concepto_pago = models.TextField(null=True)
    estado_pago = models.IntegerField(choices=ESTADOS_PAGO, default=1)


class ReciboPreinscripcion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preinscrito = models.ForeignKey(Profile, on_delete=models.CASCADE, null=False)
    preinscripcion = models.OneToOneField(Preinscripcion, on_delete=models.CASCADE, null=False)
    valor_requerido = models.FloatField(default=0)
    valor_pagado = models.FloatField(default=0)
    estado_recibo = models.IntegerField(choices=ESTADOS_RECIBO, default=2)
    valor_pagado_usuario = models.FloatField(default=0)
    valor_pagado_beca = models.FloatField(default=0)
    valor_pagado_saldo = models.FloatField(default=0)
    valor_pagado_descuento = models.FloatField(default=0)
    descuento_id = models.IntegerField(null=True)
    valor_materiales = models.FloatField(default=0)
    fecha_pago = models.DateTimeField()
    migrado = models.BooleanField(default=False)


class SaldoAFavor(Financiero):
    activo = models.BooleanField(default=False)
    recibo_preinscripcion_generado = models.ForeignKey(ReciboPreinscripcion, on_delete=models.PROTECT, null=True)
    devuelto = models.BooleanField(default=False)


class ReservasSaldo(models.Model):
    saldo = models.ForeignKey(SaldoAFavor, on_delete=models.PROTECT)
    valor = models.FloatField(null=False)
    preinscripcion_reserva = models.ForeignKey(Preinscripcion, on_delete=models.PROTECT, null=True)
    pagado = models.BooleanField(default=False)


class Pago(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    realizado_por = models.ForeignKey(Profile, related_name='pago_realizado_por', on_delete=models.CASCADE, null=True)
    financiero = models.ForeignKey(Financiero, on_delete=models.CASCADE, null=True)
    tipo_preinscripcion = models.IntegerField(choices=TIPOS_PREINSCRIPCION, default=1)
    recibo_preinscripcion = models.ForeignKey(
        ReciboPreinscripcion, on_delete=models.CASCADE, null=True, related_name='pagos'
    )
    aprobo = models.ForeignKey(Profile, related_name='pago_aprobo', on_delete=models.CASCADE, null=True)
    fecha_hora = models.DateTimeField()
    tipo = models.CharField(max_length=50, default='Pago', null=False)


class Devolucion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(Profile, related_name='devolucion_persona', on_delete=models.CASCADE, null=False)
    valor = models.IntegerField()
    saldo_a_favor = models.ForeignKey(SaldoAFavor, on_delete=models.CASCADE, null=False)
    porcentaje = models.FloatField(default=100)
    observacion = models.TextField()
    encargado = models.ForeignKey(Profile, related_name='devolucion_encargado', on_delete=models.CASCADE, null=False)

    def get_valor_devuelto(self):
        valor_devuelto = ((self.saldo_a_favor.valor * self.porcentaje)/100)
        return valor_devuelto


class CalificacionExamen(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preinscripcion_examen = models.ForeignKey(PreinscripcionExamen, on_delete=models.PROTECT, null=False)
    docente_evaluador = models.ForeignKey(Docente, on_delete=models.PROTECT, null=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, null=True)
    fecha_hora_calificacion = models.DateTimeField(null=True)

    def __str__(self):
        """
        Cadena para representar el modelo CalificacionExamen
        :return: nombre
        """
        return self.preinscripcion_examen.examen.nombre + ' ' + self.preinscripcion_examen.persona.numero_documento



class Evento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, null=True, help_text='Nombre de evento')

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Examen de Clasificacion.
        """
        return reverse('evento-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Evento
        :return: nombre
        """
        return self.nombre

class Url(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=50, default= 'Url', help_text='Identificación para URL')
    url_path = models.CharField(max_length=200, help_text='path de la URL siguiendo el siguiente patrón /*/')
    eventos = models.ManyToManyField(Evento, help_text='Eventos asociados a esta URL')

    class Meta:
        verbose_name = "URL"
        verbose_name_plural = "URLS"

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Examen de Clasificacion.
        """
        return reverse('url-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Url
        :return: nombre
        """
        return self.nombre


class EventoPeriodo(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    nombre = models.CharField(max_length=150, editable=False, default="evento", unique=False)
    alias = models.CharField(max_length=200, default="Nuevos", null=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=False, help_text='Selección de periodo')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=False, help_text='Selección de evento')
    fecha_inicio = models.DateTimeField(null=False, blank=False, help_text='Fecha y hora inicio del evento')
    fecha_final = models.DateTimeField(null=False, blank=False, help_text='fecha y hora fin del evento')

    class Meta:
        verbose_name = "Evento Periodo"
        verbose_name_plural = "Eventos Periodo"

    def save(self, *args, **kwargs):
        self.nombre = str(self.periodo.alias) + '-' + str(self.evento.nombre) + '-' + str(self.alias)
        super(EventoPeriodo, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de Evento Periodo.
        """
        return reverse('eventoperiodo-detail', args=[str(self.id)])

    def __str__(self):
        """
        Cadena para representar el modelo Url
        :return: nombre
        """
        return self.nombre


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class InformacionPreinscripcionFormalizacion(models.Model):
    documentos_pago = models.CharField(max_length=300, default='Recibo Original y copia')
    datos_pago = models.TextField(max_length=1000, default='Cuenta de ahorros')
    fecha_citacion = models.CharField(max_length=300, default='Oficina de extensión')
    lugar_citacion = models.CharField(max_length=300, default='Oficina de extensión')
    horario_citacion = models.TextField(max_length=1000, default='De 8 am a 6 pm')
    periodo = models.OneToOneField(Periodo, on_delete=models.PROTECT, help_text='Selección de periodo', unique=True)
    mensaje_formalizacion = RichTextField(blank=True, null=True, verbose_name="Instrucciones Formalización (Solo cursos)")
    link_carga_documentos = models.URLField(_("Link carga de documentos (Cursos y exámenes)"), blank=True, null=True)

    def __str__(self):
        """
        :return: nombre
        """
        return "Mensaje-" + self.periodo.alias


def usuarioTieneGrupo(usuario, nombre_grupo):
    return usuario.groups.filter(name=nombre_grupo).exists()

def getEstadoMatricula(estado):
    for e in ESTADOS_ACADEMICOS_MATRICULA:
        if e[0] == estado:
            return e[1]

def getEstadoPreinscripcion(estado):
    for e in ESTADOS_ADMINISTRATIVOS_PREINSCRIPCION:
        if e[0] == estado:
            return e[1]
    return 0

#Los modelos siguientes fueron tomados de aplicación django-survey para uso del proyecto,
# la licencia permite su modificación y uso privado
# Se puede consultar en https://github.com/Pierre-Sassoulas/django-survey/blob/master/LICENSE.txt

class Survey(models.Model):

    name = models.CharField(("Nombre"), max_length=400)
    description = models.TextField(("Descripcion"))
    is_published = models.BooleanField(("Activa"))
    is_plantilla = models.BooleanField(default=True, editable=False)

    class Meta(object):
        verbose_name = "Plantilla Encuesta"
        verbose_name_plural = "Plantillas Encuesta"

    def __str__(self):
        return self.name

    def latest_answer_date(self):
        """ Return the latest answer date.

        Return None is there is no response. """
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})


class Category(models.Model):

    name = models.CharField(("Nombre"), max_length=400)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name="Plantilla",
        related_name="categories",
    )
    order = models.IntegerField(("Mostrar Orden"), blank=True, null=True)
    description = models.CharField(
        ("Descripción"), max_length=2000, blank=True, null=True
    )

    class Meta(object):
        # pylint: disable=too-few-public-methods
        verbose_name = "Grupo de preguntas"
        verbose_name_plural = "Grupos de preguntas"

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))

try:  # pragma: no cover
    from _collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

CHOICES_HELP_TEXT = (
    """El campo de opciones es únicamente usado cuando el tipo 
    de la pregunta es 'radio' o 'selección múltiple', escriba en
    el campo la lista con las opciones separadas con coma ','
    The choices field is only used if the question type"""
)


def validate_choices(choices):
    """  Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    msg = None
    values = choices.split(settings.CHOICES_SEPARATOR)
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "El campo seleccionado requiere una lista de opciones asociada."
        msg += " Las opciones deben contener más de un ítem."
    #raise ValidationError(msg)
    return msg


class SortAnswer(object):
    CARDINAL = "cardinal"
    ALPHANUMERIC = "alfanumerico"


class Question(models.Model):

    TEXT = "texto"
    SHORT_TEXT = "texto-corto"
    RADIO = "radio"
    SELECT_MULTIPLE = "selección-múltiple"
    INTEGER = "entero"

    QUESTION_TYPES = (
        (TEXT, ("texto (múltiples líneas)")),
        (SHORT_TEXT, ("texto corto(una línea)")),
        (RADIO, ("radio")),
        (SELECT_MULTIPLE, ("Selección Múltiple")),
        (INTEGER, ("entero")),
    )

    text = models.TextField(("Texto"))
    order = models.IntegerField(("Orden"))
    required = models.BooleanField(("Obligatorio"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Grupo de preguntas",
        blank=True,
        null=True,
        related_name="questions",
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name="Encuesta",
        related_name="questions",
    )
    type = models.CharField(
        ("Tipo"), max_length=200, choices=QUESTION_TYPES, default=TEXT
    )
    choices = models.TextField(
        ("Opciones"), blank=True, null=True, help_text=CHOICES_HELP_TEXT
    )

    class Meta(object):
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ["survey", "order"]

    def clean(self,*args, **kwargs):
        if self.type in [Question.RADIO, Question.SELECT_MULTIPLE]:
            m = validate_choices(self.choices)
            if m:
                raise ValidationError(m)
            else:
                super(Question, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(settings.CHOICES_SEPARATOR):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    @property
    def answers_as_text(self):
        """ Return answers as a list of text.

        :rtype: List """
        answers_as_text = []
        for answer in self.answers.all():
            for value in answer.values:
                answers_as_text.append(value)
        return answers_as_text

    @staticmethod
    def standardize(value, group_by_letter_case=None, group_by_slugify=None):
        """ Standardize a value in order to group by slugify or letter case """
        if group_by_slugify:
            value = slugify(value)
        if group_by_letter_case:
            value = value.lower()
        return value

    @staticmethod
    def standardize_list(string_list, group_by_letter_case=None, group_by_slugify=None):
        """ Return a list of standardized string from a csv string.."""
        return [
            Question.standardize(strng, group_by_letter_case, group_by_slugify)
            for strng in string_list
        ]

    def answers_cardinality(
        self,
        min_cardinality=None,
        group_together=None,
        group_by_letter_case=None,
        group_by_slugify=None,
        filter=None,
        other_question=None,
    ):
        """ Return a dictionary with answers as key and cardinality (int or
            dict) as value

        :param int min_cardinality: The minimum of answer we need to take it
            into account.
        :param dict group_together: A dictionary of value we need to group
            together. The key (a string) is a placeholder for the list of value
            it represent (A list of string)
        :param boolean group_by_letter_case: If true we will group 'Aa' with
            'aa and 'aA'. You can use group_together as a placeholder if you
            want everything to be named 'Aa' and not 'aa'.
        :param boolean group_by_slugify: If true we will group 'Aé b' with
            'ae-b' and 'aè-B'. You can use group_together as a placeholder if
            you want everything to be named 'Aé B' and not 'ae-b'.
        :param list filter: We will exclude every string in this list.
        :param Question other_question: Instead of returning the number of
            person that answered the key as value, we will give the cardinality
            for another answer taking only the user that answered the key into
            account.
        :rtype: Dict """
        if min_cardinality is None:
            min_cardinality = 0
        if group_together is None:
            group_together = {}
        if filter is None:
            filter = []
            standardized_filter = []
        else:
            standardized_filter = Question.standardize_list(
                filter, group_by_letter_case, group_by_slugify
            )
        if other_question is not None:
            if not isinstance(other_question, Question):
                msg = "Question.answer_cardinality expect a 'Question' for "
                msg += "the 'other_question' parameter and got"
                msg += " '{}' (a '{}')".format(
                    other_question, other_question.__class__.__name__
                )
                raise TypeError(msg)
        return self.__answers_cardinality(
            min_cardinality,
            group_together,
            group_by_letter_case,
            group_by_slugify,
            filter,
            standardized_filter,
            other_question,
        )

    def __answers_cardinality(
        self,
        min_cardinality,
        group_together,
        group_by_letter_case,
        group_by_slugify,
        filter,
        standardized_filter,
        other_question,
    ):
        """ Return an ordered dict but the insertion order is the order of
        the related manager (ie question.answers).

        If you want something sorted use sorted_answers_cardinality with a set
        sort_answer parameter. """
        cardinality = OrderedDict()
        for answer in self.answers.all():
            for value in answer.values:
                value = self.__get_cardinality_value(
                    value, group_by_letter_case, group_by_slugify, group_together
                )
                if value not in filter and value not in standardized_filter:
                    user = answer.response.user
                    if other_question is None:
                        self._cardinality_plus_n(cardinality, value, 1)
                    else:
                        self.__add_user_cardinality(
                            cardinality,
                            user,
                            value,
                            other_question,
                            group_by_letter_case,
                            group_by_slugify,
                            group_together,
                            filter,
                            standardized_filter,
                        )
        if min_cardinality != 0:
            temp = {}
            for value in cardinality:
                if cardinality[value] < min_cardinality:
                    self._cardinality_plus_n(temp, "Other", cardinality[value])
                else:
                    temp[value] = cardinality[value]
            cardinality = temp
        if other_question is not None:
            # Treating the value for Other question that were not answered in
            # this question
            for answer in other_question.answers.all():
                for value in answer.values:
                    value = self.__get_cardinality_value(
                        value, group_by_letter_case, group_by_slugify, group_together
                    )
                    if value not in filter + standardized_filter:
                        if answer.response.user is None:
                            self._cardinality_plus_answer(
                                cardinality, _(settings.USER_DID_NOT_ANSWER), value
                            )
        return cardinality

    def sorted_answers_cardinality(
        self,
        min_cardinality=None,
        group_together=None,
        group_by_letter_case=None,
        group_by_slugify=None,
        filter=None,
        sort_answer=None,
        other_question=None,
    ):
        """ Mostly to have reliable tests, but marginally nicer too...

        The ordering is reversed for same cardinality value so we have aa
        before zz. """
        cardinality = self.answers_cardinality(
            min_cardinality,
            group_together,
            group_by_letter_case,
            group_by_slugify,
            filter,
            other_question,
        )
        # We handle SortAnswer without enum because using "type" as a variable
        # name break the enum module and we want to use type in
        # answer_cardinality for simplicity
        possibles_values = [SortAnswer.ALPHANUMERIC, SortAnswer.CARDINAL, None]
        undefined = sort_answer is None
        user_defined = isinstance(sort_answer, dict)
        valid = user_defined or sort_answer in possibles_values
        if not valid:
            msg = "Unrecognized option '%s' for 'sort_answer': " % sort_answer
            msg += "use nothing, a dict (answer: rank),"
            for option in possibles_values:
                msg += " '{}', or".format(option)
            msg = msg[:-4]
            msg += ". We used the default cardinal sorting."
            LOGGER.warning(msg)
        if undefined or not valid:
            sort_answer = SortAnswer.CARDINAL
        sorted_cardinality = None
        if user_defined:
            sorted_cardinality = sorted(
                list(cardinality.items()), key=lambda x: sort_answer.get(x[0], 0)
            )
        elif sort_answer == SortAnswer.ALPHANUMERIC:
            sorted_cardinality = sorted(cardinality.items())
        elif sort_answer == SortAnswer.CARDINAL:
            if other_question is None:
                sorted_cardinality = sorted(
                    list(cardinality.items()), key=lambda x: (-x[1], x[0])
                )
            else:
                # There is a dict instead of an int
                sorted_cardinality = sorted(
                    list(cardinality.items()), key=lambda x: (-sum(x[1].values()), x[0])
                )
        return OrderedDict(sorted_cardinality)

    def _cardinality_plus_answer(self, cardinality, value, other_question_value):
        """ The user answered 'value' to our question and
        'other_question_value' to the other question. """
        if cardinality.get(value) is None:
            cardinality[value] = {other_question_value: 1}
        elif isinstance(cardinality[value], int):
            # Previous answer did not had an answer to other question
            cardinality[value] = {
                _(settings.USER_DID_NOT_ANSWER): cardinality[value],
                other_question_value: 1,
            }
        else:
            if cardinality[value].get(other_question_value) is None:
                cardinality[value][other_question_value] = 1
            else:
                cardinality[value][other_question_value] += 1

    def _cardinality_plus_n(self, cardinality, value, n):
        """ We don't know what is the answer to other question but the
        user answered 'value'. """
        if cardinality.get(value) is None:
            cardinality[value] = n
        else:
            cardinality[value] += n

    def __get_cardinality_value(
        self, value, group_by_letter_case, group_by_slugify, group_together
    ):
        """ Return the value we should use for cardinality. """
        value = Question.standardize(value, group_by_letter_case, group_by_slugify)
        for key, values in list(group_together.items()):
            grouped_values = Question.standardize_list(
                values, group_by_letter_case, group_by_slugify
            )
            if value in grouped_values:
                value = key
        return value

    def __add_user_cardinality(
        self,
        cardinality,
        user,
        value,
        other_question,
        group_by_letter_case,
        group_by_slugify,
        group_together,
        filter,
        standardized_filter,
    ):
        found_answer = False
        for other_answer in other_question.answers.all():
            if user is None:
                break
            elif other_answer.response.user == user:
                # We suppose there is only a response per user
                # Why would you want this info if it is
                # possible to answer multiple time ?
                found_answer = True
                break
        if found_answer:
            values = other_answer.values
        else:
            values = [(settings.USER_DID_NOT_ANSWER)]
        for other_value in values:
            other_value = self.__get_cardinality_value(
                other_value, group_by_letter_case, group_by_slugify, group_together
            )
            if other_value not in filter + standardized_filter:
                self._cardinality_plus_answer(cardinality, value, other_value)

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        msg = "Question '{}' ".format(self.text)
        if self.required:
            msg += "(*) "
        msg += "{}".format(self.get_clean_choices())
        return msg


class Response(models.Model):

    """
        A Response object is a collection of questions and answers with a
        unique interview uuid.
    """

    created = models.DateTimeField(("Fecha de creación"), auto_now_add=True)
    updated = models.DateTimeField(("Fecha de actualización"), auto_now=True)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name="Encuesta",
        related_name="responses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Usuario",
        null=True,
        blank=True,
    )
    interview_uuid = models.CharField(("Identificador único de diligenciamiento"), max_length=36)

    class Meta(object):
        verbose_name = "Diligenciamiento"
        verbose_name_plural = "Diligenciamientos"

    def __str__(self):
        msg = "Diligenciamiento a {} por {}".format(self.survey, self.user)
        msg += " en {}".format(self.created)
        return msg


class Answer(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Pregunta",
        related_name="answers",
    )
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        verbose_name="Diligenciamiento",
        related_name="answers",
    )
    created = models.DateTimeField(("Fecha de creación"), auto_now_add=True)
    updated = models.DateTimeField(("Fecha de actualización"), auto_now=True)
    body = models.TextField(("Contenido"), blank=True, null=True)

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super(Answer, self).__init__(*args, **kwargs)

    @property
    def values(self):
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        #  We do not use eval for security reason but it could work with :
        #  eval(self.body)
        #  It would permit to inject code into answer though.
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT_MULTIPLE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = "Respuesta imposible '{}'".format(body)
                    msg += " debe estar en {} ".format(choices)
                    raise ValidationError(msg)

    def __str__(self):
        return "{} to '{}' : '{}'".format(
            self.__class__.__name__, self.question, self.body
        )


class AsociarEncuesta(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, help_text='Selección de periodo')
    plantilla = models.ForeignKey(Survey, on_delete=models.PROTECT, help_text='Selección de plantilla de encuesta')
    programas = models.ManyToManyField(ProgramaAcademico, help_text="Seleccione Programas Academicos")

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular de asociar encuesta.
        """
        return reverse('asociar_update', args=[str(self.id)])

    def __str__(self):
        return "{} - {}".format(
            self.periodo.alias, self.plantilla.name
        )


class Encuesta(Survey):
    programa = models.ForeignKey(ProgramaAcademico, on_delete=models.PROTECT)
    asociada = models.ForeignKey(AsociarEncuesta, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Encuesta"
        verbose_name_plural = "Encuestas"

    def __str__(self):
        return "{} - {} - {}".format(
            self.asociada.periodo.alias, self.asociada.plantilla.name, self.programa.nombre,
        )


class ReporteHermesConfiguracion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_inicio = models.DateField(default=timezone.now, help_text="Fecha Inicio del Reporte HERMES")
    fecha_final = models.DateField(default=timezone.now, help_text="Fecha Final del Reporte HERMES")

    class Meta:
        verbose_name = "reporte_hermes_configuracion"
        verbose_name_plural = "reporte_hermes_configuraciones"

    def get_absolute_url(self):
        """
         Devuelve la url para acceder a una instancia particular de Periodo.
         """
        return reverse('reporte_hermes')

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(ReporteHermesConfiguracion, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


auditlog.register(Profile)
auditlog.register(User)
auditlog.register(PersonaContacto)
auditlog.register(Pago)
auditlog.register(SaldoAFavor)
auditlog.register(Devolucion)
auditlog.register(AutorizadoCurso)
auditlog.register(PreinscripcionHorarioCurso)
auditlog.register(PreinscripcionExamen)
