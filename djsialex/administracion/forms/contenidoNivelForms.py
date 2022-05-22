from django import forms
from ..models import ContenidoNivel, ContenidoNivelVersion
from bootstrap_modal_forms.forms import BSModalForm


class ContenidoNivelForm(forms.ModelForm):

    class Meta:
        model = ContenidoNivel
        fields = ('alias',)


class ContenidoNivelVersionForm(forms.ModelForm):

    class Meta:
        model = ContenidoNivelVersion
        fields = ('alias','documento')


class ContenidoNivelVersionFormUpdate(BSModalForm):

    class Meta:
        model = ContenidoNivelVersion
        fields = ('alias','documento')

