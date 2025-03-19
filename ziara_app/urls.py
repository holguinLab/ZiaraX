from django.urls import path
from . views import *

urlpatterns=[
    path('',index,name='index'),
    
    # PANEL DE SESION
    path('login',login,name='login'),
    path('register/',register,name='register'),
    
    # PANEL ADMIN 
    path('admin_panel/',admin_panel,name='admin_panel'),
    #-----> CRUD : USUARIOS <------- 
    path('listar_usuarios/',listar_usuarios,name='listar_usuarios'),
    
    # PANEL DE USUARIO
    path('logout/',logout,name='logout'),
    path('recuperar_password/',recueperar_password,name='recuperar_password'),
    path('verificacion_token_recuperar_password/',verificacion_token_recuperar_password,name='verificacion_token_recuperar_password')
]
