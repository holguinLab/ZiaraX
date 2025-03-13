from django.urls import path
from . views import *

urlpatterns=[
    path('',login,name='login'),
    path('index/',index,name='index'),
    path('admin_panel/',admin_panel,name='admin_panel'),
    path('logout/',logout,name='logout'),
    path('register/',register,name='register'),
    path('recuperar_password/',recueperar_password,name='recuperar_password'),
    path('verificacion_token_recuperar_password/',verificacion_token_recuperar_password,name='verificacion_token_recuperar_password')
]
