from django.contrib import admin
from . models import *
# Register your models here.

@admin.register(Usuarios)
class adminUsuarios(admin.ModelAdmin):
    list_display=['id','email','password','nombre_completo','tipoUsuario','foto','token_recuperar_clave','username']
    list_editable=['email','password','password','nombre_completo','tipoUsuario','foto','username']

@admin.register(Barberos)
class adminBarberos(admin.ModelAdmin):
    list_display=['id','usuario_barbero','admin_creador','horario_trabajo','especialidad','experiencia']
    list_editable=['usuario_barbero','admin_creador','horario_trabajo','especialidad','experiencia']

@admin.register(Servicios)
class adminServicios(admin.ModelAdmin):
    list_display=['id','nombre','precio','duracion']
    list_editable=['nombre','precio','duracion']

@admin.register(Citas)
class adminCitas(admin.ModelAdmin):
    list_display=['id','cliente','barbero','estado','fecha']
    list_editable=['cliente','barbero','estado']


@admin.register(CitaServicios)
class adminCitaServicios(admin.ModelAdmin):
    list_display=['id','cita','servicio']
    list_editable=['cita']
    
@admin.register(Clientes)
class adminClientes(admin.ModelAdmin):
    list_display=['id','usuario_cliente']
    list_editable=['usuario_cliente']
