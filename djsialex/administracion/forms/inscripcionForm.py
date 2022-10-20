from django import forms

from administracion.models import PreinscripcionHorarioCurso, Idioma, ProgramaAcademico, Nivel, Curso, OfertaAcademica, \
    HorarioCurso, PreinscripcionExamen


class PreinscripcionCursoForm(forms.ModelForm):

    idioma = forms.ModelChoiceField(
        queryset=Idioma.objects.filter(
            programaacademico__activo=True,
            programaacademico__ofertaacademica__periodo__activo=True,
            programaacademico__ofertaacademica__periodo__finalizado=False
        ).prefetch_related(
            'programaacademico_set',
            'programaacademico_set__ofertaacademica_set'
        ).distinct().order_by(
            'nombre'
        )
    )

    class Meta:
        pass
        model = PreinscripcionHorarioCurso
        exclude = ['horario_cupo','persona','estado_preinscripcion','estado_matriculado','fecha_preinscripcion', 'descuento_solicitado', 'valor_preinscripcion', 'codigo_hash']


class PreinscripcionExamenForm(forms.ModelForm):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all().order_by('nombre'))

    class Meta:
        model = PreinscripcionExamen
        exclude = ['examen', 'persona', 'estado_preinscripcion', 'fecha_preinscripcion', 'valor_preinscripcion', 'codigo_hash']


class PreinscripcionCursoLoteForm(forms.Form):

    idioma = forms.ModelChoiceField(queryset=Idioma.objects.all().order_by('nombre'))
    archivo = forms.FileField(required=True)
