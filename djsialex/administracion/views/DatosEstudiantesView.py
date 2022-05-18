from ..models import DatosEstudiantesModel
from ..serialize import DatosEstudiantesSerialize
from rest_framework import viewsets


class DatosEstudiantesAPI(viewsets.ModelViewSet):
    queryset = DatosEstudiantesModel.objects.raw('select * from datosEstudiantes(\'2021-01-01\',\'2021-12-31\')')
    serializer_class = DatosEstudiantesSerialize

