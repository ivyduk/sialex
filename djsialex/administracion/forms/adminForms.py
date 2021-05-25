from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError

from ..models import Franja, Horario

DIAS = {
    'Lunes' : [0, 'LU'],
    'Martes' : [1, 'MA'],
    'Miercoles' : [2,'MC'],
    'Jueves' : [3, 'JU'],
    'Viernes' : [4, 'VI'],
    'Sabado' : [5, 'SA'],
    'Domingo' : [6, 'DO'],
}

class HorarioAdminForm(ModelForm):

    horario_str = ''

    def getIndex(self, key):
        return DIAS[key][0]

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            Horario.objects.get(nombre=cleaned_data['horario_str'])
        except Horario.DoesNotExist:
            pass
        else:
            raise ValidationError('Ya existe un horario con las mismas franjas creadas')


    def clean_franja(self):
        franjas_aux = self.cleaned_data['franja']
        horario_dict = {}

        for f in franjas_aux.all():
            franjas_aux = f.nombre.split('-')
            hora = franjas_aux[1] + '-' + franjas_aux[2]
            dia = franjas_aux[0]
            if hora not in horario_dict:
                horario_dict[hora] = []
            horario_dict[hora].append(dia)

        hor_str = ''

        for horario in horario_dict:
            dias = horario_dict[horario]
            horario_dict[horario] = sorted(dias, key=self.getIndex)
            dias = horario_dict[horario]
            hor_str += horario + ":" + ','.join([DIAS[dia][1] for dia in dias]) + '; '

        self.horario_str = hor_str[:len(hor_str)-2]
        if Horario.objects.filter(nombre=self.horario_str).exists():
            self.cleaned_data['horario_str'] = None
            raise forms.ValidationError("Ya se ha guardado un horario con las mismas franjas.")
        else:
            self.cleaned_data['franjas'] = self.cleaned_data['franja']
            self.cleaned_data['horario_str'] = self.horario_str

    def clean_alias(self):
        alias = self.cleaned_data['alias']
        if Horario.objects.filter(alias=alias).exists():
            raise forms.ValidationError("Ya se ha guardado un horario con este alias.")
        return alias

    class Meta:
        model = Horario
        exclude = ['nombre']


