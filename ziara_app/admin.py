from django.contrib import admin
from . models import *
# Register your models here.

@admin.register(Usuarios)
class adminUsuarios(admin.ModelAdmin):
    list_display=['id','email','password','nombre_completo','tipoUsuario','foto']
    list_editable=['email','password','password','nombre_completo','tipoUsuario','foto']
