from django import forms
from bootstrap_datepicker_plus import DateTimePickerInput

from administracion.models import reporteHermes_conf

class ReporteFechaForm(forms.ModelForm):
    class Meta:
        model = reporteHermes_conf
        fields = '__all__'
        FORMAT = '%Y-%m-%d'
        widgets = {'fecha_inicio': DateTimePickerInput(format=FORMAT),
                   'fecha_final': DateTimePickerInput(format=FORMAT),
                   }

    def clean(self):
        cleaned_data = super(ReporteFechaForm, self).clean()
        return cleaned_data
        