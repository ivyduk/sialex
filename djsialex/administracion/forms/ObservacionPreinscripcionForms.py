from django import forms
from ..models import Preinscripcion

class ObservacionPreinscripcionForm(forms.Form):
    observaciones = forms.CharField(widget=forms.Textarea)
