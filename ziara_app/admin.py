from django.contrib import admin
from . models import *
# Register your models here.

@admin.register(Usuarios)
class adminUsuarios(admin.ModelAdmin):
    list_display=['id','email','password','nombre_completo','tipoUsuario','foto','token_recuperar_clave','username']
    list_editable=['email','password','password','nombre_completo','tipoUsuario','foto','username']

@admin.register(Barberos)
class adminBarberos(admin.ModelAdmin):
    list_display=['id','usuario_barbero','admin_creador','horario_trabajo','especialidad']
    list_editable=['usuario_barbero','admin_creador','horario_trabajo','especialidad']