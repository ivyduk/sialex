import os

from django.contrib import admin
from django.contrib.admin import AdminSite

from administracion.forms import HorarioAdminForm

from .models import *

from django.contrib.auth.models import User, Group



admin.site.register(Pais)
admin.site.register(Ciudad)
admin.site.register(Periodicidad)
admin.site.register(EscalaNota)
admin.site.register(Nivel)
admin.site.register(ProgramaAcademico)
admin.site.register(Idioma)
admin.site.register(NotaParcial)
admin.site.register(TipoDocumentoIdentidad)
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

class SalonAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edificio']

admin.site.register(Salon , SalonAdmin)

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
	list_display = ('alias', 'secuencia', 'anio','secuencia')


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

from .encuesta_actions import  activar_plantillas
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


