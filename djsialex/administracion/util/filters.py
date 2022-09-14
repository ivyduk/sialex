from ..models import Periodo, OfertaAcademica, ExamenClasificacion
import django_filters


class PeriodoFilter(django_filters.FilterSet):
    alias = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Periodo
        fields = ['anio','periodicidad','alias',]


class OfertaFilter(django_filters.FilterSet):
    anio = django_filters.CharFilter(field_name='periodo__anio' , lookup_expr='iexact')
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = OfertaAcademica
        fields = ['anio', 'periodo__periodicidad_id', 'nombre']


class ExamenFilter(django_filters.FilterSet):
    anio = django_filters.CharFilter(field_name='periodo__anio', lookup_expr='iexact')
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ExamenClasificacion
        fields = ['anio', 'periodo__periodicidad_id', 'nombre']
