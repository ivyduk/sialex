from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput
from django import forms

from ..models import Profile, Discapacidad
from ..forms import DireccionField, DireccionSelectorWidget

class SinBordeTextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['style'] = 'border: none !important;'
        self.attrs['style'] += 'outline: none !important;'


class PersonaAdministracionForm(forms.ModelForm):

    segundo_nombre = forms.CharField(required=False)
    segundo_apellido = forms.CharField(required=False)
    es_egresado = forms.TypedChoiceField(
        initial='No',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Si')),
        label='Es egresado de la UNAL'
    )
    discapacidad = forms.ModelChoiceField(queryset=Discapacidad.objects.order_by('nombre'), required=False)
    direccion_sin_formato = DireccionField(widget=DireccionSelectorWidget(), required=False, label='Dirección de residencia')
    edad = forms.CharField(label='Edad',required=False,widget=SinBordeTextInput(attrs={'readonly': 'readonly'}))


    class Meta:
        model = Profile
        exclude = ['usuario', 'numero_documento','profile_completed', 'cuenta_duplicada',
                   'cuenta_duplicada_desactivada', 'acepta_habeas_data', 'indicativo_celular',
                   'indicativo_fijo', 'email_confirmed', 'direccion_residencia']

        FORMAT = '%Y-%m-%d'

        widgets = {'fecha_nacimiento' : DatePickerInput(format=FORMAT),
                   }

        labels = {
            'fecha_nacimiento': 'Fecha de nacimiento',
            'ciudad_expedicion_documento': 'Ciudad de expedición de documento',
            'genero_sexual': 'Sexo Biológico',
            'pais_nacimiento': 'País de nacimiento',
            'ciudad_nacimiento': 'Ciudad de nacimiento',
            'pais_residencia': 'País de residencia',
            'ciudad_residencia': 'Ciudad de residencia',
            'direccion_sin_formato': 'Dirección de residencia actual',
            'telefono_fijo': 'Teléfono fijo',
            'telefono_celular': 'Teléfono celular',
            'tipo_sangre': 'Tipo de sangre',
            'eps': 'EPS',
            'tipo_vinculacion_un': 'Tipo de vinculación UN',
            'nivel_formacion': 'Nivel de formación',
            'numero_documento': 'Documento de identidad',
            'profile_active': 'Perfil Activo',
            'documento_identificacion_entregado': 'Documento identificación entregado',
            'es_egresado': 'Es egresado UN',
            'estado_civil': 'Estado civil'
        }

    def clean(self):

        cleaned_data = super(PersonaAdministracionForm, self).clean()
        return cleaned_data
    
