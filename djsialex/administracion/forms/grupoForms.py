from optparse import Option
import uuid

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from bootstrap_datepicker_plus import DatePickerInput
from ..models import GrupoAcademico, Matricula, Docente, Salon, Edificio, DocentesGrupoAcademico

class GrupoAcademicoForm(forms.ModelForm):
    class Meta:
        model = GrupoAcademico
        fields = ('nombre', 'codigo_proyecto', 'horarioCurso','fecha_inicio', 'fecha_final')
        widgets = {'horarioCurso': forms.HiddenInput(),
                   'fecha_inicio': forms.HiddenInput(),
                   'fecha_final': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(GrupoAcademicoForm, self).__init__(*args, **kwargs)
        self.fields['horarioCurso'].label = ''
        self.fields['fecha_inicio'].label = ''
        self.fields['fecha_final'].label = ''

class CambioGrupoForm(forms.Form):
    matriculas = forms.ModelMultipleChoiceField(queryset=Matricula.objects.none(),
                                                required=False,
                                                widget=FilteredSelectMultiple("Matriculas", is_stacked=False))

    def __init__(self, grupo_id, *args, **kwargs):
        super(CambioGrupoForm, self).__init__(*args, **kwargs)
        self.fields['matriculas'].queryset = Matricula.objects.filter(grupo_id=grupo_id, estado_matricula__in=[1,2,7,8])

class AsignarSalonDocenteAGrupoForm(forms.Form):
    FORMAT = '%Y-%m-%d'
    docentes_generales = forms.ModelMultipleChoiceField(queryset=Docente.objects.none(), required= False)
    docentes_especializados = forms.ModelMultipleChoiceField(queryset=Docente.objects.none(), required=False)
    edificio = forms.ModelChoiceField(queryset=Edificio.objects.all(), required=False)
    salones = forms.ModelMultipleChoiceField(queryset=Salon.objects.all(), required=False)
    observaciones = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 200}), required=False)
    codigo_proyecto = forms.CharField(widget=forms.TextInput())
    fecha_inicio = forms.DateField(widget= DatePickerInput(format=FORMAT))
    fecha_final = forms.DateField(widget= DatePickerInput(format=FORMAT))

    def __init__(self, grupo_id, *args, **kwargs):
        super(AsignarSalonDocenteAGrupoForm, self).__init__(*args, **kwargs)
        docentes_en_grupo_general = DocentesGrupoAcademico.objects.filter(grupo_academico_id=grupo_id, tipo_docente__id=1).values_list('docente__id', flat=True)
        docentes_en_grupo_especializado = DocentesGrupoAcademico.objects.filter(grupo_academico_id=grupo_id, tipo_docente__id=2).values_list(
            'docente__id', flat=True)
        self.fields['docentes_generales'].queryset = Docente.objects.exclude(id__in=docentes_en_grupo_general).filter(activo=True).order_by('persona__primer_nombre', 'persona__primer_apellido')
        self.fields['docentes_especializados'].queryset = Docente.objects.exclude(id__in=docentes_en_grupo_especializado).filter(activo=True).order_by('persona__primer_nombre', 'persona__primer_apellido')
        try:
            grupo = GrupoAcademico.objects.get(pk=grupo_id)
        except GrupoAcademico.DoesNotExist:
            grupo = None
        if grupo and grupo.observaciones:
            self.fields['observaciones'].initial = grupo.observaciones
        if grupo.codigo_proyecto:
            self.fields['codigo_proyecto'].initial = grupo.codigo_proyecto
        if grupo.fecha_inicio:
            self.fields['fecha_inicio'].initial = grupo.fecha_inicio
        if grupo.fecha_final:
            self.fields['fecha_final'].initial = grupo.fecha_final
