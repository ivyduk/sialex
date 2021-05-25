from bootstrap_datepicker_plus import DateTimePickerInput
from captcha.fields import CaptchaField
from django import forms
from django.forms.formsets import BaseFormSet
from django.contrib.auth.models import User

from ..models import TipoDocumentoIdentidad, PersonaContacto, Pais, Ciudad, Profile, EPS
from django.db.models import Q


class EditProfileForm(forms.ModelForm):
    segundo_apellido = forms.CharField(help_text='Ingrese el primer apellido', required=False)
    segundo_nombre = forms.CharField(help_text='Ingrese el segundo apellido', required=False)
    eps = forms.ModelChoiceField(queryset=EPS.objects.order_by('nombre'))

    def clean_telefono_fijo(self):
        tel_fijo = str(self.cleaned_data['telefono_fijo']).split('+')[1]
        return tel_fijo

    def clean_telefono_celular(self):
        tel_celular = str(self.cleaned_data['telefono_celular']).split('+')[1]
        return tel_celular

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = kwargs.pop('user', None)
        self.fields['eps'].queryset = self.fields['eps'].queryset.order_by('nombre')

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['primer_nombre', 'primer_apellido', 'fecha_nacimiento', 'indicativo_fijo', 'indicativo_celular',
                   'personas_de_contacto', 'email_confirmed', 'profile_completed', 'usuario', 'tipo_documento',
                   'numero_documento', 'profile_active', 'cuenta_duplicada', 'cuenta_duplicada_desactivada',
                   'acepta_habeas_data', 'documento_identificacion_entregado']

        labels = {
            'fecha_nacimiento': 'Fecha de nacimiento',
            'ciudad_expedicion_documento': 'Ciudad de expedición de documento',
            'genero_sexual': 'Sexo Biológico',
            'pais_nacimiento': 'País de nacimiento',
            'ciudad_nacimiento': 'Ciudad de nacimiento',
            'pais_residencia': 'País de residencia',
            'ciudad_residencia': 'Ciudad de residencia',
            'direccion_residencia': 'Dirección de residencia actual',
            'telefono_fijo': 'Teléfono fijo',
            'telefono_celular': 'Teléfono celular',
            'tipo_sangre': 'Tipo de sangre',
            'eps': 'EPS',
            'tipo_vinculacion_un': 'Tipo de vinculación UN',
            'nivel_formacion': 'Nivel de formación'
        }

        FORMAT = '%Y-%m-%d'
        widgets = {'fecha_nacimiento': DateTimePickerInput(format=FORMAT),}


class PersonaContactoForm(forms.ModelForm):

    class Meta:
        model = PersonaContacto
        fields = '__all__'
        exclude = ['profile']


class BasePersonaContactoFormSet(BaseFormSet):
    def clean(self):
        pass

    def __init__(self, *args, **kwargs):
        super(BasePersonaContactoFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
