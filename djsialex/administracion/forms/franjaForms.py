from django import forms

from administracion.models import Franja


class FranjaCreateForm(forms.ModelForm):

    class Meta:
        model = Franja
        fields = '__all__'
