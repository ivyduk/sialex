from django import forms
from django.forms import inlineformset_factory
from ..models import ConjuntoNotas, NotaParcial, EscalaNota

class NotaParcialForm(forms.ModelForm):

    nombre = forms.CharField(widget=forms.TextInput(), help_text='Nombre de la nota a evaluar')
    ponderacion = forms.IntegerField(label='Ponderación (%)', widget=forms.NumberInput(attrs={"class" : "ponderacion"}),help_text='la suma de las ponderaciones debe ser 100')
    descripcion = forms.CharField(widget=forms.TextInput())

    class meta:
        model = NotaParcial
        fields = ['nombre', 'tipo_nota', 'descripcion', 'ponderacion', 'orden_nota_conjunto']


NotaParcialFormset = inlineformset_factory(
    ConjuntoNotas, NotaParcial, form=NotaParcialForm, fields=['nombre', 'tipo_nota', 'descripcion', 'ponderacion', 'orden_nota_conjunto'], extra=1, can_delete=True)

class ConjuntoNotasForm(forms.ModelForm):

    class Meta:
        model = ConjuntoNotas
        fields = '__all__'
