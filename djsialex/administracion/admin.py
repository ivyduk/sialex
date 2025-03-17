import os

from django.contrib import admin
from django.contrib.admin import AdminSite

from administracion.forms import HorarioAdminForm

from .models import *

from django.contrib.auth.models import User, Group

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
admin.site.register(HorarioCurso)
admin.site.register(ConjuntoNotas)
admin.site.register(Descuento)
admin.site.register(Docente)
admin.site.register(Edificio)
admin.site.register(Discapacidad)
admin.site.register(EPS)
admin.site.register(InformacionPreinscripcionFormalizacion)


class TipoDocumentoIdentidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'activo']

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TipoDocumentoIdentidad, TipoDocumentoIdentidadAdmin)


class PaisAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'hermes_id']


admin.site.register(Pais, PaisAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'pais_id', 'hermes_id']
    list_filter = ['pais']


admin.site.register(Region, RegionAdmin)


class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id', 'hermes_id']
    list_filter = ['region']


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
    readonly_fields = ('calificacionFinal', "grupo_id", "grupo", "preinscripcion_generada", "estudiante")


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


