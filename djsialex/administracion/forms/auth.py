from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from bootstrap_datepicker_plus import DateTimePickerInput
from django.forms.formsets import BaseFormSet


from ..models import TipoDocumentoIdentidad


class SignUpForm(UserCreationForm):
    FORMAT = '%Y-%m-%d'
    tipo_documento = forms.ModelChoiceField(queryset=TipoDocumentoIdentidad.objects.filter(activo=True), empty_label="--Seleccione tipo de documento--")
    numero_documento = forms.CharField(help_text='Ingrese el número de documento')
    primer_apellido = forms.CharField(help_text='Ingrese el primer nombre')
    primer_nombre = forms.CharField(help_text='Ingrese el segundo nombre')
    segundo_apellido = forms.CharField(help_text='Ingrese el primer apellido',required = False)
    segundo_nombre = forms.CharField(help_text='Ingrese el segundo apellido',required = False)
    acepta_habeas_data = forms.BooleanField(help_text='Acepta la política de tratamiento de datos personales', required=True)
    fecha_nacimiento = forms.DateTimeField(widget=DateTimePickerInput(format=FORMAT))
    email2 = forms.CharField(initial='')

    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('tipo_documento',
                  'numero_documento',
                  'primer_apellido',
                  'primer_nombre',
                  'segundo_apellido',
                  'segundo_nombre',
                  'email',
                  'acepta_habeas_data',
                  'fecha_nacimiento',
                  )

    def clean_email2(self):

        email = self.cleaned_data['email']
        email2 = self.cleaned_data['email2']

        if email != email2:
            raise forms.ValidationError("Los correos electrónicos no son iguales")
        
        return email2
