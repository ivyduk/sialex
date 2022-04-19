from ..models import DatosEstudiantesModel
from ..serialize import DatosEstudiantesSerialize
from rest_framework import viewsets


class DatosEstudiantesAPI(viewsets.ModelViewSet):
    queryset = DatosEstudiantesModel.objects.raw('select * from datosEstudiantes(\'2022-01-01\',\'2022-04-30\')')
    serializer_class = DatosEstudiantesSerialize