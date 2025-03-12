from django.urls import path
from . views import *

urlpatterns=[
    path('',login,name='login'),
    path('index/',index,name='index'),
    path('admin_panel/',admin_panel,name='admin_panel'),
    path('logout/',logout,name='logout')
]
