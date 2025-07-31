
from django.contrib import admin
from django import forms

from administracion.forms import HorarioAdminForm

from .models import *


admin.site.register(Periodicidad)
admin.site.register(EscalaNota)
admin.site.register(Nivel)
admin.site.register(ProgramaAcademico)
admin.site.register(Idioma)
admin.site.register(NotaParcial)
admin.site.register(DocumentoIdentidad)
admin.site.register(DocumentoRequerido)
admin.site.register(Franja)
admin.site.register(OfertaAcademica)
admin.site.register(Curso)
admin.site.register(ConjuntoNotas)
admin.site.register(Descuento)
admin.site.register(Docente)
admin.site.register(Edificio)
admin.site.register(Discapacidad)
admin.site.register(EPS)
admin.site.register(InformacionPreinscripcionFormalizacion)


def close_availability(modeladmin, request, queryset):
    for obj in queryset:
        obj.cupo_disponible = 0
        obj.save()

close_availability.short_description = "Cerrar cupos de inscripcion"


class PeriodoFilter(admin.SimpleListFilter):
    title = 'Filtro Periodo Activo'
    parameter_name = 'periodo_activo'

    def lookups(self, request, model_admin):
        return (
            ('activo', 'periodo activo'),
            ('finalizado', 'Periodo Finalizado'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(curso__oferta_academica__periodo__activo=True)
        elif self.value() == 'finalizado':
            return queryset.filter(curso__oferta_academica__periodo__finalizado=True)
        return queryset


class HorarioCursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cupo_disponible', 'preinscritos']
    search_fields = ('nombre',)
    list_filter = (PeriodoFilter, 'curso__nivel__orden', 'curso__oferta_academica__programa', "curso__oferta_academica__periodo__anio")
    actions = [close_availability]

    def preinscritos(self, obj):
        preinscritos_horario_curso = PreinscripcionHorarioCurso.objects.filter(horario_cupo_id=obj.id,
                                                                               estado_preinscripcion__in=[1, 3]).all()  # estados: Inscrito, Pendiente
        return preinscritos_horario_curso.__len__()


admin.site.register(HorarioCurso, HorarioCursoAdmin)


class TipoDocumentoIdentidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'activo']

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TipoDocumentoIdentidad, TipoDocumentoIdentidadAdmin)


class PaisAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'hermes_id']
    search_fields = ('nombre',)


admin.site.register(Pais, PaisAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'pais_id', 'hermes_id']
    list_filter = ['pais']
    search_fields = ('nombre',)


admin.site.register(Region, RegionAdmin)


class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'hermes_id']
    list_filter = ['region']
    search_fields = ('nombre',)


admin.site.register(Ciudad, CiudadAdmin)


class SalonAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edificio']


admin.site.register(Salon, SalonAdmin)


class GrupoAcademicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'codigo_proyecto']
    search_fields = ('id', 'codigo', 'nombre')
    exclude = ['horarioCurso']
    readonly_fields = ('nombre', "salones", )


admin.site.register(GrupoAcademico, GrupoAcademicoAdmin)

class DescuentoAplicadoAdmin(admin.ModelAdmin):
    list_display = (
        'id',                # si tienes un campo id
        'beneficiario',      # campo heredado de Financiero
        'periodo_generado',  # campo heredado de Financiero
        'valor',             # campo heredado de Financiero
    )
    list_filter = ('periodo_generado__anio', 'estado_descuento',)
    readonly_fields = ( 'beneficiario','periodo_generado', 'preinscripcion_generada', 'valor',)
    search_fields = ('beneficiario__numero_documento',)

admin.site.register(DescuentoAplicado, DescuentoAplicadoAdmin)

class ComprobanteBancoAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiario', 'periodo_generado', 'valor',)
    readonly_fields = ( 'beneficiario','periodo_generado', 'preinscripcion_generada', 'valor',)
    search_fields = ('beneficiario__numero_documento',)
    list_filter = ('periodo_generado__anio',)

admin.site.register(ComprobanteBanco, ComprobanteBancoAdmin)

class ReservasSaldoInline(admin.TabularInline):  # Usa StackedInline si prefieres un diseño vertical
    model = ReservasSaldo
    extra = 0  # Número de filas vacías para agregar nuevas reservas
    fields = ('id', 'saldo', 'valor', 'preinscripcion_reserva', 'pagado')  # Campos que deseas mostrar
    readonly_fields = ('saldo', 'preinscripcion_reserva', 'valor', 'pagado',)  # Si quieres que algunos campos sean solo de lectura
    can_delete = False

class SaldoAFavorAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiario', 'periodo_generado', 'valor',)
    readonly_fields = ( 'beneficiario','periodo_generado', 'recibo_preinscripcion_generado',  'devuelto', 'valor', )
    search_fields = ('beneficiario__numero_documento',)
    list_filter = ('activo', 'periodo_generado__anio',)
    inlines = [ReservasSaldoInline]

admin.site.register(SaldoAFavor, SaldoAFavorAdmin)

class PagoForm(forms.ModelForm):
    valor = forms.FloatField(label="Valor", required=False)

    class Meta:
        model = Pago
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.financiero:
            self.fields['valor'].initial = self.instance.financiero.valor

    def save(self, commit=True):
        instance = super().save(commit=False)
        valor = self.cleaned_data.get('valor')
        if instance.financiero and valor is not None:
            instance.financiero.valor = valor
            instance.financiero.save()
        if commit:
            instance.save()
        return instance

class PagoAdmin(admin.ModelAdmin):
    form = PagoForm
    list_display = [
        'valor',
        'beneficiario',
        'tipo',      
        'get_periodo_nombre',
        'get_estado_preinscripcion', 
        'aprobo',
     ]
    search_fields = ('realizado_por__numero_documento',)
    readonly_fields = ('aprobo', 'beneficiario','get_periodo_nombre', 'recibo_preinscripcion', 'realizado_por', 'financiero', )
    list_filter = ('tipo', )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos (Financieros)"

    def get_estado_preinscripcion(self, obj):
        return obj.recibo_preinscripcion.preinscripcion.get_estado_preinscripcion()

    def periodo_generado(self, obj):
        return obj.financiero.periodo_generado

    def get_periodo_nombre(self, obj):
        return obj.financiero.periodo_generado.nombre
    
    def beneficiario(self, obj):
        return obj.financiero.beneficiario.primer_nombre + " " + obj.financiero.beneficiario.primer_apellido
    
    def valor(self, obj):
        return obj.financiero.valor if obj.financiero and obj.financiero.valor else "No disponible"
    


admin.site.register(Pago, PagoAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'id', 'primer_nombre',
                    'primer_apellido')
    search_fields = ('numero_documento', 'primer_nombre', 'primer_apellido')
    readonly_fields = ('direccion_sin_formato', 'usuario')


@admin.register(PreinscripcionHorarioCurso)
class PreinscripcionCursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_preinscripcion', 'persona',
                    'estado_preinscripcion', 'valor_preinscripcion', 'requiere_facturacion',
                    'horario_cupo')
    search_fields = ( 'id', 'persona__numero_documento')
    readonly_fields = ('valor_preinscripcion', 'codigo_hash', "persona")


@admin.register(PreinscripcionExamen)
class PreinscripcionExamenAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_preinscripcion', 'persona',
                    'estado_preinscripcion', 'valor_preinscripcion', 'requiere_facturacion')
    search_fields = ('id', 'persona__numero_documento')
    readonly_fields = ('valor_preinscripcion', 'codigo_hash', "persona", "examen")


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
	list_display = ('alias', 'secuencia', 'anio','secuencia', 'nombre')


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'estado_matricula', 'calificacionFinal')
    search_fields = ('estudiante__numero_documento', )
    readonly_fields = ('calificacionFinal', "estudiante")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj and obj.preinscripcion_generada and obj.preinscripcion_generada.preinscripcionhorariocurso:
            # Filtrar los grupos según la preinscripción del objeto
            form.base_fields['grupo'].queryset = GrupoAcademico.objects.filter(
                horarioCurso__curso__oferta_academica__periodo__inicio__gte=obj.preinscripcion_generada.preinscripcionhorariocurso.horario_cupo.curso.oferta_academica.periodo.inicio,
            )
            form.base_fields['preinscripcion_generada'].queryset = Preinscripcion.objects.filter(
                persona=obj.preinscripcion_generada.persona
            )
        else:
            # Comportamiento por defecto si no hay objeto
            form.base_fields['grupo'].queryset = GrupoAcademico.objects.none()
            form.base_fields['preinscripcion_generada'].queryset = Preinscripcion.objects.none()

        return form


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
	form = HorarioAdminForm

	def save_related(self, request, form, formsets, change):
		horario = form.instance
		if form.cleaned_data['horario_str']:
			horario.nombre = form.cleaned_data['horario_str']
			horario.franja.set(form.cleaned_data['franjas'])
			if form.is_valid():
				horario.save()


from .models import Answer, Category, Question, Response, Survey

from .encuesta_actions import activar_plantillas
from functools import partial


class QuestionInline(admin.TabularInline):
    model = Question
    ordering = ["order", "category"]
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(QuestionInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        survey = kwargs.pop('obj', None)
        formfield = super(QuestionInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "category" and survey:
            formfield.queryset = Category.objects.filter(survey=survey)
        elif db_field.name == "category" and not survey:
            formfield.queryset = Category.objects.none()
        return formfield


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = ["name", "is_published"]
    list_filter = ["is_published"]
    inlines = [CategoryInline, QuestionInline]
    actions = [activar_plantillas]

    def get_queryset(self, request):
        qs = super(SurveyAdmin, self).get_queryset(request)
        return qs.filter(is_plantilla=True)


class AnswerBaseInline(admin.StackedInline):
    fields = ["question", "body"]
    readonly_fields = ["question",]
    extra = 0
    model = Answer


class ResponseAdmin(admin.ModelAdmin):
    list_display = ["interview_uuid", "survey", "created", "user"]
    list_filter = ["survey", "created"]
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ["survey", "created", "updated", "interview_uuid", "user"]


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Encuesta)


