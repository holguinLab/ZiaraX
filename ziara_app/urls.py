from django.urls import path
from . views import *

urlpatterns=[
    path('',index,name='index'),

    #Esta ruta es la que retorna un json para usarlo en la api de pixaby 
    path('obtener_servicios/',obtener_servicios,name='obtener_servicios'),
    path('obtener_productos/',obtener_productos,name='obtener_productos'),
    
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
    path('eliminar_servicio/<int:id_servicio>/',eliminar_servicio,name='eliminar_servicio'),

    #PRODUCTOS
    path('listar_productos/',listar_productos,name='listar_productos'),
    path('nuevo_producto/',nuevo_producto,name='nuevo_producto'),
    path('detalle_producto/<int:id_producto>/',detalle_producto,name='detalle_producto'),
    path('eliminar_producto/<int:id_producto>/',eliminar_producto,name='eliminar_producto'),
    
    #CITAS 
    path('listar_citas/',listar_citas,name='listar_citas'),
    
    #NOTIFICACIONES
    path('ultimos_datos_admin/',ultimos_datos_admin,name='ultimos_datos_admin'),
    
    
    
    
    #INVENTARIO
    path('inventario/',inventario,name='inventario'),
    
    #endregion

    #region CLIENTES
    
    # region Citas
    path('reservas_citas/',reservas_citas,name='reservas_citas'),
    path('registrar_citas/',registrar_citas,name='registrar_citas'),
    path('agregar_servicio_carrito/<int:servicio_id>/',agregar_servicio_carrito,name='agregar_servicio_carrito'),
    path('eliminar_elementos_carrito/<int:servicio_id>/',eliminar_elementos_carrito,name='eliminar_elementos_carrito'),
    path('ver_citas/',ver_citas,name='ver_citas'),
    path('confirmar_citas/<int:id_cita>/',confirmar_citas,name='confirmar_citas'),
    path('cancelar_citas/<int:id_cita>/',cancelar_citas,name='cancelar_citas'),
    
    #endregion
    
    # region Productos
    path('ver_tienda/',ver_tienda,name='ver_tienda'),
    path('agregar_productos_carrito/<int:id_producto>/',agregar_productos_carrito,name='agregar_productos_carrito'),

    #endregion
    #endregion
    
    # region PANEL DE USUARIO
    path('logout/',logout,name='logout'),
    path('recuperar_password/',recueperar_password,name='recuperar_password'),
    path('verificacion_token_recuperar_password/',verificacion_token_recuperar_password,name='verificacion_token_recuperar_password'),
    path('ver_perfil/<int:id_usuario>/',ver_perfil,name='ver_perfil'),
    #endregion
]

