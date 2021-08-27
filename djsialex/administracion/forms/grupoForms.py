import uuid

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import GrupoAcademico, Matricula, Docente, Salon, Edificio, DocentesGrupoAcademico


class GrupoAcademicoForm(forms.ModelForm):
    class Meta:
        model = GrupoAcademico
        fields = ('nombre', 'codigo_proyecto', 'horarioCurso')
        widgets = {'horarioCurso': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(GrupoAcademicoForm, self).__init__(*args, **kwargs)
        self.fields['horarioCurso'].label = ''



class CambioGrupoForm(forms.Form):
    matriculas = forms.ModelMultipleChoiceField(queryset=Matricula.objects.none(),
                                                required=False,
                                                widget=FilteredSelectMultiple("Matriculas", is_stacked=False))

    def __init__(self, grupo_id, *args, **kwargs):
        super(CambioGrupoForm, self).__init__(*args, **kwargs)
        self.fields['matriculas'].queryset = Matricula.objects.filter(grupo_id=grupo_id, estado_matricula__in=[1,2,7,8])

class AsignarSalonDocenteAGrupoForm(forms.Form):

    docentes_generales = forms.ModelMultipleChoiceField(queryset=Docente.objects.none(), required= False)
    docentes_especializados = forms.ModelMultipleChoiceField(queryset=Docente.objects.none(), required=False)
    edificio = forms.ModelChoiceField(queryset=Edificio.objects.all(), required=False)
    salones = forms.ModelMultipleChoiceField(queryset=Salon.objects.all(), required=False)
    observaciones = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 200}), required=False)

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
