from django.forms import ModelForm
from django import forms

from administracion.models import Nivel, Idioma

class NivelForm(ModelForm):

    def clean(self):

        cleaned_data = super().clean()
        orden = self.cleaned_data['orden']
        idioma = self.cleaned_data['idioma']
        alias = self.cleaned_data['alias']
        predecesor_alias = self.cleaned_data['predecesor']

        if orden < 1:
            self.add_error('orden', 'El orden debe ser mayor a 0')

        alias_encontrado = Nivel.objects.filter(alias__exact=alias)
        if len(alias_encontrado) != 0:
            self.add_error('alias', 'Un nivel con el mismo alias ya existe')

        if predecesor_alias != None:
            predecesor = Nivel.objects.get(alias__exact=predecesor_alias)

            if predecesor != None:

                if predecesor.idioma == idioma:
                    if predecesor.orden >= orden:
                        self.add_error('predecesor', 'El predecesor debe tener un orden menor')

                    nivel_encontrado = Nivel.objects.filter(predecesor__alias=predecesor_alias, orden = orden)
                    if len(nivel_encontrado) != 0:
                        raise forms.ValidationError('Un nivel con el mismo predecesor y el mismo orden ya existe')

                else:
                    self.add_error('predecesor', 'El predecesor debe tener el mismo idioma')

        else: #No escoge predecesor y el orden es mayor a 1, entonces deberia ser el primero
            if orden > 1:
                self.add_error('orden', 'El orden debe ser 1, dado que no tiene predecesor')


        return cleaned_data

    class Meta:
        model = Nivel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NivelForm, self).__init__(*args, **kwargs)
        self.fields['edad_minima'].widget.attrs['min'] = 1
        self.fields['edad_minima'].widget.attrs['oninput'] = "validity.valid||(value='');"
        self.fields['edad_maxima'].widget.attrs['min'] = 1
        self.fields['edad_maxima'].widget.attrs['oninput'] = "validity.valid||(value='');"