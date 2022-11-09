from bootstrap_datepicker_plus import DateTimePickerInput
from captcha.fields import CaptchaField
from django import forms
from django.forms.formsets import BaseFormSet
from django.contrib.auth.models import User
from administracion.enums import *
from django.utils.safestring import mark_safe

from ..models import TipoDocumentoIdentidad, PersonaContacto, Pais, Ciudad, Profile, EPS
from django.db.models import Q


class DireccionSelectorWidget(forms.widgets.MultiWidget):
    
    def __init__(self, attrs=None ):  
        
        widgets = (
            forms.widgets.Select(attrs={'class':'input-address'}, choices=DIRECCION_TIPO),
            forms.widgets.NumberInput(attrs={'class':'input-address','maxlength':3,'min':1,'max':200}),
            forms.widgets.Select(attrs={'class':'input-address','maxlength':1}, choices=DIRECCION_LETRA),
            forms.widgets.Select(attrs={'class':'input-address'}, choices=DIRECCION_PREFIJO), 
            forms.widgets.TextInput(attrs={'class':'input-addressNumber','readonly':'readonly', 'placeholder':'N°'}),
            forms.widgets.NumberInput(attrs={'class':'input-address','maxlength':3,'min':1,'max':200}),
            forms.widgets.Select(attrs={'class':'input-address','maxlength':1}, choices=DIRECCION_LETRA),
            forms.widgets.Select(attrs={'class':'input-address'}, choices=DIRECCION_PREFIJO), 
            forms.widgets.NumberInput(attrs={'class':'input-address','maxlength':3,'min':1,'max':200}),
            forms.widgets.TextInput(attrs={'class':'input-addressAdi'}),
            )
        super(DireccionSelectorWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split("|")
        return [None, None]

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)

    def render(self, name, value, attrs=None, renderer=None):
        """Copy and past from original render method"""
        
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
                       
            if i == 0:
                attrs_required = True
                attrs_style    = "width: 110"
            if i in (1,5,8):
                attrs_required = True
                attrs_style    = "width:  45; text-align: center"
            if i in (2,6):
                attrs_required = False
                attrs_style    = "width:  35; text-align: center"
            if i in (3,7): 
                attrs_required = False
                attrs_style    = "width:  90"
            if i == 4: 
                attrs_required = False
                attrs_style    = "width:  20"
            if i == 9: 
                attrs_required = False
                attrs_style    = "width:  100%"

            final_attrs = dict(final_attrs, required = attrs_required, style = attrs_style)                  
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            
        return mark_safe(self.format_output(output))

class DireccionField(forms.fields.MultiValueField):
    widget = DireccionSelectorWidget

    def __init__(self, *args, **kwargs):

        fields = (
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField(),
                forms.CharField()
            )
        super(DireccionField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        print(data_list)
        return "|".join(data_list)

class EditProfileForm(forms.ModelForm):
    segundo_apellido = forms.CharField(help_text='Ingrese el primer apellido', required=False)
    segundo_nombre = forms.CharField(help_text='Ingrese el segundo apellido', required=False)
    eps = forms.ModelChoiceField(queryset=EPS.objects.order_by('nombre'))
    direccion_residencia = DireccionField(widget = DireccionSelectorWidget())
    es_egresado = forms.TypedChoiceField(
        initial='No',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Si'))
    )
    telefono_celular = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[0-9]{10}'}))

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
            'es_egresado': 'Es egresado UN',
            'estado_civil': 'Estado civil'
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
