from django import forms
from django.forms import inlineformset_factory, BaseModelFormSet

from ..models import Curso, OfertaAcademica, Nivel, ConjuntoNotas, HorarioCurso, Horario

class HorarioCursoForm(forms.ModelForm):

    horario = forms.ModelChoiceField(queryset=Horario.objects.all(), required=True, widget=forms.Select(attrs={"class" : "form-control"}))
    cupo_inicial = forms.IntegerField( widget=forms.NumberInput(attrs={}))

    class meta:
        model = HorarioCurso


    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if HorarioCurso.objects.filter(nombre=nombre).exists():
            raise forms.ValidationError("Ya se ha guardado un horario curso con este nombre.")
        return nombre


HorarioCursoFormset = inlineformset_factory(
    Curso, HorarioCurso, form=HorarioCursoForm,
    fields=['horario', 'cupo_inicial', 'cupo_autorizados'],extra=1, can_delete=True)

class CursoModelForm(forms.ModelForm):
    oferta_academica = forms.ModelChoiceField(queryset=OfertaAcademica.objects.all().order_by('nombre'),widget=forms.Select(attrs={"class" : "form-control"}))
    nivel = forms.ModelChoiceField(queryset=Nivel.objects.all().order_by('idioma__nombre', 'orden'), widget=forms.Select(attrs={"class" : "form-control"}))
    conjunto_notas = forms.ModelChoiceField(queryset=ConjuntoNotas.objects.all(), widget=forms.Select(attrs={"class" : "form-control"}))

    class Meta:
        model = Curso
        fields = ('oferta_academica', 'nivel', 'conjunto_notas')
        labels = {
            'oferta_academica' : 'Oferta Academica',
            'nivel' : 'Nivel',
            'conjunto_notas' : 'Conjunto de Notas para este nivel'
        }
