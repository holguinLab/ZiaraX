from rest_framework import serializers
from .models import *


#

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        #fields = "__all__"
        fields = "__all__"



class ServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = ['id','nombre','precio']