from django.forms import ModelForm
from django import forms

from ..models import OfertaAcademica

class OfertaAcademicaCreateForm(ModelForm):

    class Meta:
        model = OfertaAcademica
        fields = '__all__'

    def clean_programa(self):
        nombre = str(self.cleaned_data['periodo']) + '-' + str(self.cleaned_data['programa'])
        programa = self.cleaned_data['programa']
        if OfertaAcademica.objects.filter(nombre=nombre).exists():
            raise forms.ValidationError("Ya se ha guardado una oferta académica con este programa y período.")
        return programa