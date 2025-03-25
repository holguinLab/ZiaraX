from django.urls import path
from . views import *

urlpatterns=[
    path('',index,name='index'),
    
    # PANEL DE SESION
    path('login/',login,name='login'),
    path('register/',register,name='register'),
    
    
    
    #region PANEL ADMIN 
    path('admin_panel/',admin_panel,name='admin_panel'),
    
    # USUARIOS 
    path('listar_usuarios/',listar_usuarios,name='listar_usuarios'),
    path('detalles_barberos/<int:id_barbero>/',detalles_barberos,name='detalles_barberos'),
    
    #SERVICIOS
    path('listar_servicios/',listar_servicios,name='listar_servicios'),
    path('nuevo_servicio/',nuevo_servicio,name='nuevo_servicio'),
    
    #CITAS 
    path('listar_citas/',listar_citas,name='listar_citas'),
    
    #NOTIFICACIONES
    path('ultimos_datos_admin/',ultimos_datos_admin,name='ultimos_datos_admin'),
    #endregion


    #RESERVAS 
    path('reservas_citas/',reservas_citas,name='reservas_citas'),
    path('registrar_citas/',registrar_citas,name='registrar_citas'),
    
    
    # region PANEL DE USUARIO
    path('logout/',logout,name='logout'),
    path('recuperar_password/',recueperar_password,name='recuperar_password'),
    path('verificacion_token_recuperar_password/',verificacion_token_recuperar_password,name='verificacion_token_recuperar_password'),
    path('ver_perfil/<int:id_usuario>/',ver_perfil,name='ver_perfil'),
    #endregion
]

