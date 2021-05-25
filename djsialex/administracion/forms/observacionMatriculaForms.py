from bootstrap_modal_forms.forms import BSModalForm
from django import forms

from administracion.models import Observacion


class ObservacionMatriculaForm(forms.ModelForm):

    class Meta:
        model = Observacion
        exclude = ['persona_asignadora', 'matricula', 'fecha_actualizacion']

        labels = { 'observacion': 'Observación'}

class ObservacionMatriculaUpdateForm(BSModalForm):

    class Meta:
        model = Observacion
        exclude = ['persona_asignadora', 'matricula', 'fecha_actualizacion']

        labels = {'observacion': 'Observación'}