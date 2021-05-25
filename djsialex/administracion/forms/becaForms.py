from django import forms

from administracion.models import TipoBeca, Beca, Nivel


class TipoBecaForm(forms.ModelForm):

    class Meta:
        model = TipoBeca
        fields = '__all__'

        labels = {'porcentaje': 'Porcentaje (%)'}


    def __init__(self, *args, **kwargs):
        super(TipoBecaForm, self).__init__(*args, **kwargs)
        self.fields['porcentaje'].widget.attrs['min'] = 0


class BecaForm(forms.ModelForm):

    class Meta:
        model = Beca
        exclude = ['beneficiario', 'periodo_generado', 'asignada_por', 'fecha_asignacion', 'estado_beca', 'valor']

    def __init__(self, niveles, niveles_seleccionados, *args, **kwargs):
        super(BecaForm, self).__init__(*args, **kwargs)
        ids_niveles = [niveles[idioma].id for idioma in niveles]
        self.fields['nivel_idioma'].queryset = Nivel.objects.filter(id__in=ids_niveles)
