from django import forms
from bootstrap_datepicker_plus import DateTimePickerInput

from administracion.models import Periodo


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = '__all__'
        FORMAT = '%Y-%m-%d'
        widgets = {'fecha_inicio': DateTimePickerInput(format=FORMAT),
                   'fecha_final': DateTimePickerInput(format=FORMAT),
                   'fecha_pendientes': DateTimePickerInput(format=FORMAT)
                   }

    def clean(self):
        cleaned_data = super(PeriodoForm, self).clean()

        abierto = cleaned_data.get('abierto')
        periodicidad = cleaned_data.get('periodicidad')
        secuencia = cleaned_data.get('secuencia')

        # Values may be None if the fields did not pass previous validations.
        if abierto is not None and periodicidad is not None:
            if abierto and periodicidad.nombre != 'Bimestral' and periodicidad.nombre != 'Semestral':
                self.add_error('periodicidad', 'Los Períodos Regulares solo permiten Periodicidad Semestral o Bimestral')
            if abierto and periodicidad.nombre == 'Bimestral' and (secuencia < 1 or secuencia > 4):
                self.add_error('secuencia',
                               'Los Períodos Bimestrales solo permiten secuencia entre 1 y 4')
            if abierto and periodicidad.nombre == 'Semestral' and (secuencia < 1 or secuencia > 2):
                self.add_error('secuencia',
                               'Los Períodos Semestrales solo permiten secuencia entre 1 y 2')
        return cleaned_data
