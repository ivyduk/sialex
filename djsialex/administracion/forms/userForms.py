from django.contrib.auth.forms import AuthenticationForm
from django import forms
from ..models import Periodo


class UserAuthenticationWithCaptchaForm(AuthenticationForm):
    """tipo_documento = forms.ModelChoiceField(queryset=TipoDocumentoIdentidad.objects.all(),
                                            empty_label="--Tipo documento--")
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.filter(activo=True, finalizado=False),
                                            empty_label="--Seleccione periodo--")"""
    numero_documento = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Número de documento'}))
