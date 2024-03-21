from django import forms

from administracion.models import PreinscripcionHorarioCurso, Idioma, ProgramaAcademico, Nivel, Curso, OfertaAcademica, \
    HorarioCurso, PreinscripcionExamen, Preinscripcion, Idioma, Periodo


class PreinscripcionCursoForm(forms.ModelForm):

    modalidad = forms.ModelChoiceField(
        queryset=Periodo.objects.filter(
            activo=True,
            finalizado=False
        ).distinct().order_by(
            'nombre'
        )
    )

    class Meta:
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


class ObservacionPreinscripcionForm(forms.ModelForm):

    class Meta:
        model = Preinscripcion
        exclude = [
            'horario_cupo',
            'persona',
            'estado_preinscripcion',
            'estado_matriculado',
            'fecha_preinscripcion',
            'descuento_solicitado',
            'valor_preinscripcion',
            'codigo_hash',
            'requiere_facturacion'
        ]