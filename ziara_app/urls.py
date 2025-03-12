from django.urls import path
from . views import *

urlpatterns=[
    path('',login,name='login'),
    path('index/',index,name='index'),
    path('formularios/',formularios,name='formularios'),
    path('data_tables/',data_tables,name='data_tables'),
    path('servicio_barba/',servicio_barba,name='servicio_barba'),
    path('servicio_corte/',servicio_corte,name='servicio_corte'),
    path('servicio_spa/',servicio_spa,name='servicio_spa'),
    path('producto_aceite/',producto_aceite,name='producto_aceite'),
    path('producto_crema/',producto_crema,name='producto_crema'),
    path('producto_locion/',producto_locion,name='producto_locion'),
    path('admin_panel/',admin_panel,name='admin_panel'),
    path('carrito/',carrito,name='carrito'),
]
