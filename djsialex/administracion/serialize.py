from rest_framework import serializers
from .models import *

class DatosEstudiantesSerialize(serializers.ModelSerializer):
    class Meta:
        model  =  DatosEstudiantesModel
        fields = '__all__'

