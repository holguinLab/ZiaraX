# Importacion de librerias
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages 
from .models import * # Importacion de todos los modelos en models.py
from .utils import * # Importacion de la funcion de incriptacion y verificacion del archivo utils.py
from django.db import IntegrityError
from django.http import JsonResponse # para convertir la lista de notificacines en un json para trabajarla con ajax
from datetime import datetime

# Libreria para validacion de correos email y mensaje de error cuando no es correo 
from django.core.exceptions import ValidationError  # Se usa para Hacer validaciones de campos especificos 
from django.core.validators import validate_email # Se usa para validar si un campo es un correo 
# region PILLOW # ! Librerias Para usar PILLOW 🏙️ 
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io

import os
from django.conf import settings
from django.core.files import File

import uuid
import re
#endregion

#region ENVIOCORREO 
from django.core.mail import send_mail
#endregion

#region PROCESO DE IMAGENES
def hacer_imagen_redonda(imagen, tamaño=(500, 500)):
    """
    Procesa la imagen para hacerla circular y del tamaño especificado.
    Retorna un objeto de archivo listo para ser guardado en el modelo.
    """
    # Abrir la imagen
    img = Image.open(imagen).convert("RGBA")
    
    # Redimensionar la imagen
    img = img.resize(tamaño, Image.LANCZOS)

    # Crear máscara circular
    mascara = Image.new("L", tamaño, 0)
    draw = ImageDraw.Draw(mascara)
    draw.ellipse((0, 0, tamaño[0], tamaño[1]), fill=255)

    # Aplicar la máscara
    imagen_circular = Image.new("RGBA", tamaño, (0, 0, 0, 0))
    imagen_circular.paste(img, (0, 0), mask=mascara)

    # Guardar en memoria
    buffer = io.BytesIO()
    imagen_circular.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
#endregion

# Esta funcion solo muestra el index.html cuando se llama 
def index(request):
    verificar = request.session.get('logueado',{})
    if verificar.get('rol') == 'B':
        return redirect('panel_barbero')
    elif verificar.get('rol') == 'A':
        return redirect('admin_panel')
    servicios = Servicios.objects.all()
    productos = Productos.objects.order_by('-id')[:3]
    ultimos_servicios= Servicios.objects.order_by('-id')[:3]
    barberos = Barberos.objects.all()
    carrito_id = request.session.get('carrito_servicios',[])
    carrito_producto_id = request.session.get('carrito_productos',[])
    
    carrito_servicios = Servicios.objects.filter(id__in = carrito_id) # Filter devuelve una lista 
    carrito_productos = Productos.objects.filter(id__in = carrito_producto_id)
    
    suma = len(carrito_productos) + len(carrito_servicios)
    contexto = {
        'carrito_servicios' :carrito_servicios,
        'carrito_productos' :carrito_productos,
        'suma' :suma,
        'servicios':servicios,
        'productos':productos,
        'barberos':barberos,
        'ultimos_servicios' : ultimos_servicios,
    }
    return render(request,'index.html',contexto)

# vista que convierte la consulta de servicios en json para que la podamos usar en el script(js) de index_servicios.js
def obtener_servicios(request):
    servicios = Servicios.objects.all().values('id','img_url')
    return JsonResponse(list(servicios), safe=False) 

def obtener_productos(request):
    productos = Productos.objects.all().values('id','img_url')
    return JsonResponse(list(productos), safe=False) 

#region CLIENTES

#region Citas

def reservas_citas (request):
    verificar = request.session.get('logueado',{})
    carrito_id = request.session.get('carrito_servicios',[])
    if not verificar or verificar['rol'] == 'C':
        
        barberos = Barberos.objects.all()
        servicios = Servicios.objects.all()
        
        carrito_id = request.session.get('carrito_servicios',[])
        carrito_producto_id = request.session.get('carrito_productos',[])
        carrito_servicios = Servicios.objects.filter(id__in = carrito_id) # Filter devuelve una lista 
        carrito_productos = Productos.objects.filter(id__in = carrito_producto_id)
        suma = len(carrito_productos) + len(carrito_servicios)
        
        contexto ={
            'carrito_servicios' :carrito_servicios,
            'carrito_productos' :carrito_productos,
            'suma' :suma,
            'barberos' : barberos,
            'servicios' :servicios,
        }
        return render(request,'reservas/reservas_citas.html',contexto)
    if verificar.get('rol') != 'C':
        messages.warning(request,'⚠️ WARNING : No Puedes Hacer Esto')
        return redirect('index')

def agregar_servicio_carrito(request,servicio_id): # servicio_id que viene del html
    # Si no hay session de loguedo aparece un errro y redirije a index
    verificar = request.session.get('logueado',False)
    if not verificar:
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    #Si la session tiene como rol administrador o barbero tampoco tendra permitido agregar servicios al carrito
    elif verificar['rol'] != 'C':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        #Se obtiene y se compara el servicio con el id del servicio en el modelo con el id  que se ingresa en el html
        # servicio = Servicios.objects.get(id=servicio_id) es lo mismo que usar la funcion get_objects_404
        servicio = get_object_or_404(Servicios,id=servicio_id)
        
        #Si no hay una sesion con el nombre carrito_servicios
        if 'carrito_servicios' not in request.session:
            request.session['carrito_servicios'] = [] #Creamos la sesion carrito_servicios que sera igual a una lista vacia
        
        carrito = request.session['carrito_servicios'] #asigno una variable a esa sesion que creamos en este caso la llame igual
        
        #si el servicio_id no esta en la lista carrito se agrega , asi se evitan duplicados de servicios
        if servicio_id not in carrito:
            carrito.append(servicio_id)
        
        request.session["carrito_servicios"] = carrito  # Guardar en sesión
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    #Exepcion si el id ingresado en l html no se encuentra en el id del modelo 
    except Servicios.DoesNotExist:
        messages.info(request,'❌ ERROR : No Hay Datos Asociados')
    except Exception as e:
        messages.info(request,f'❌ ERROR : {e}')
    return redirect('index')

def eliminar_elementos_carrito(request,servicio_id):
    #Creacion de varible para saber si dentro de la sesiones hay una que se llama carrito_servicios
    verificar_carrito = request.session.get('carrito_servicios',False)
    #creacion de variable para saber si dentro de las sesiones hay una que se llama logueado 
    verificar = request.session.get('logueado',False)
    if not verificar :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    elif verificar['rol'] != 'C':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        if verificar_carrito: # si existe guardo la sesion en una varible 
            carrito_servicios = request.session['carrito_servicios']
            # comparo si el id que se obtiene desde el html esta en la lista de carrito_servicios
            if servicio_id in carrito_servicios :
                #Si esta uso el metdo de listas romove para eliminarlo
                carrito_servicios.remove(servicio_id)
                #Guardar los cambios en la sesion llamada carrito_servicios 
                request.session['carrito_servicios'] = carrito_servicios
        # Redirige a la página anterior (o a 'index' si no hay referencia)
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    except Servicios.DoesNotExist:
        messages.error(request,f'❌ ERROR : No Hay Datos Asociados')
    except Exception as e:
        messages.error(request,f'❌ ERROR : {e}')
    return redirect('index')

def registrar_citas(request):
    verificar = request.session.get('logueado',False)
    verificar_carrito = request.session.get('carrito_servicios',False)
    if request.method == 'POST' :
        if verificar and verificar['rol'] == 'C':
            barbero_id = request.POST.get('barbero')  # Recibir el ID del barbero
            try:
                usuario = Usuarios.objects.get(pk = verificar['id'])
                cliente = Clientes.objects.get(usuario_cliente = usuario)
                barbero = Barberos.objects.get(pk=barbero_id)
                cita = Citas(
                    barbero=barbero,
                    cliente=cliente,
                    estado='PEN',
                    fecha = request.POST.get('fecha')
                )
                cita.save()
                # si hay  una session con carrito_servicios si no redirigimos
                if verificar_carrito:
                    #recorremos la lista
                    print(verificar_carrito)
                    for servicio_id in request.session['carrito_servicios']:
                        servicio = Servicios.objects.get(id = servicio_id)
                        #Creamos la cita servicio con la instancia de la cita de arriba y el servicio
                        cita_servicio = CitaServicios(
                            cita = cita,
                            servicio = servicio
                        )
                        cita_servicio.save()
                    #vaciamos el carrito con los servicios cuanto se agrega a cita servicios
                    request.session['carrito_servicios'] = []
                    messages.success(request,' ✅ MENSAJE :  Cita Agendada Con Exito ')
                    return redirect('index')
                return redirect('index')
            except Citas.DoesNotExist:
                messages.warning(request,'❌ ERROR :No hay Datos Sobre Citas Asociadas')
            except Usuarios.DoesNotExist:
                messages.warning(request,'❌ ERROR :No hay Datos Sobre Usuarios  Asociados')
            except Barberos.DoesNotExist:
                messages.info(request,'ℹ️ INFO : Por Favor Selecciona Un Barbero. ')
            except Servicios.DoesNotExist:
                messages.warning(request,'❌ ERROR :No hay Datos Sobre Servicios Asociados')
            except Exception as e:
                messages.warning(request,f'❌ ERROR :{e}')
            return redirect('reservas_citas')
        else:
            messages.info(request,'❌ ERROR : No Tienes Permitido Hacer Esto')
            return redirect('login')
    return redirect('index')

def ver_citas(request):
    verificar =request.session.get('logueado',{})
    if verificar.get('rol') == 'C':
        try:
            usuario = Usuarios.objects.get(pk = verificar['id'])
            cliente = usuario.clientes.first()
            
            
            carrito_id = request.session.get('carrito_servicios',[])
            carrito_producto_id = request.session.get('carrito_productos',[])
            
            
            carrito_servicios = Servicios.objects.filter(id__in = carrito_id) # Filter devuelve una lista 
            carrito_productos = Productos.objects.filter(id__in = carrito_producto_id)
            suma = len(carrito_productos) + len(carrito_servicios)
            
            contexto={
                'carrito_servicios' :carrito_servicios,
                'carrito_productos' :carrito_productos,
                'suma' :suma,
                'cliente' : cliente
            }
            return render(request,'clientes/ver_citas.html',contexto)
        except Usuarios.DoesNotExist:
            messages.info(request,' ❌ ERROR : No Hay Datos Sobre Usuarios Asociados')
        except Exception as e:
            messages.info(request,f' ❌ ERROR : {e}')
        return redirect('index')
    else:
        messages.warning(request,'❌ ERROR: No Tienes Permito Hacer Esto')
        return redirect('index')

def confirmar_citas(request,id_cita):
    verificar = request.session.get('logueado',{})
    if verificar.get('rol') == 'C':
        try:
            cita = Citas.objects.get(pk = id_cita)
            cita.estado = 'PRO'
            cita.save()
            return redirect('ver_citas')
        except Citas.DoesNotExist:
            messages.info(request,' ❌ ERROR : No Hay Datos Sobre Citas Asociados')
        except Exception as e:
            messages.info(request,f' ❌ ERROR : {e}')
        return redirect('index')
    else:
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')

def cancelar_citas(request,id_cita):
    verificar = request.session.get('logueado',{})
    if verificar.get('rol') == 'C':
        try:
            cita = Citas.objects.get(pk = id_cita)
            cita.delete()
            return redirect('ver_citas')
        except Citas.DoesNotExist:
            messages.info(request,' ❌ ERROR : No Hay Datos Sobre Citas Asociados')
        except Exception as e:
            messages.info(request,f' ❌ ERROR : {e}')
        return redirect('index')
    else:
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
#endregion

# region Productos
def ver_tienda(request):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] == 'C' :
        ultimos_productos = Productos.objects.order_by('-id')[:3]
        productos = Productos.objects.all()
        
        # Obtener parámetros de búsqueda y categoría
        buscar = request.GET.get('buscar')
        categoria = request.GET.get('categoria')

        if buscar:
            productos = productos.filter(nombre__icontains=buscar)

        if categoria:
            productos = productos.filter(categoria=categoria)
        
        
        carrito_id = request.session.get('carrito_servicios',[])
        carrito_producto_id = request.session.get('carrito_productos',[])
        carrito_servicios = Servicios.objects.filter(id__in = carrito_id) # Filter devuelve una lista 
        carrito_productos = Productos.objects.filter(id__in = carrito_producto_id)
        suma = len(carrito_productos) + len(carrito_servicios)
        contexto = {
            'carrito_servicios' :carrito_servicios,
            'carrito_productos' :carrito_productos,
            'ultimos_productos':ultimos_productos,
            'suma' : suma,
            'productos': productos
        }
        return render(request,'clientes/ver_tienda.html',contexto)
    else:
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')


def agregar_productos_carrito(request,id_producto):
    # Si no hay session de loguedo aparece un errro y redirije a index
    verificar = request.session.get('logueado',False)
    if not verificar:
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    #Si la session tiene como rol administrador o barbero tampoco tendra permitido agregar servicios al carrito
    elif verificar['rol'] != 'C':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        #Se obtiene y se compara el servicio con el id del servicio en el modelo con el id  que se ingresa en el html
        # servicio = Servicios.objects.get(id=servicio_id) es lo mismo que usar la funcion get_objects_404
        producto = Productos.objects.get(id = id_producto)
        
        #Si no hay una sesion con el nombre carrito_servicios
        if 'carrito_productos' not in request.session:
            request.session['carrito_productos'] = [] #Creamos la sesion carrito_servicios que sera igual a una lista vacia
        
        carrito_productos = request.session['carrito_productos'] #asigno una variable a esa sesion que creamos en este caso la llame igual
        
        #si el servicio_id no esta en la lista carrito se agrega , asi se evitan duplicados de servicios
        if id_producto not in carrito_productos:
            carrito_productos.append(id_producto)
        
        request.session["carrito_productos"] = carrito_productos  # Guardar en sesión
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    #Exepcion si el id ingresado en l html no se encuentra en el id del modelo 
    except Productos.DoesNotExist:
        messages.info(request,'❌ ERROR : No Hay Datos Asociados')
    except Exception as e:
        messages.info(request,f'❌ ERROR : {e}')
    return redirect('index')

def eliminar_productos_carrito(request,id_producto):
    #Creacion de varible para saber si dentro de la sesiones hay una que se llama carrito_servicios
    verificar_carrito = request.session.get('carrito_productos',False)
    #creacion de variable para saber si dentro de las sesiones hay una que se llama logueado 
    verificar = request.session.get('logueado',False)
    if not verificar :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    elif verificar['rol'] != 'C':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        if verificar_carrito: # si existe guardo la sesion en una varible 
            carrito_productos = request.session['carrito_productos']
            # comparo si el id que se obtiene desde el html esta en la lista de carrito_servicios
            if id_producto in carrito_productos :
                #Si esta uso el metdo de listas romove para eliminarlo
                carrito_productos.remove(id_producto)
                #Guardar los cambios en la sesion llamada carrito_servicios 
                request.session['carrito_productos'] = carrito_productos
        # Redirige a la página anterior (o a 'index' si no hay referencia)
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    except Servicios.DoesNotExist:
        messages.error(request,f'❌ ERROR : No Hay Datos Sobre Servicios Asociados')
    except Exception as e:
        messages.error(request,f'❌ ERROR : {e}')
    return redirect('index')
#endregion

#endregion

#region BARBEROS
def panel_barbero(request):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'B':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        usuario = Usuarios.objects.get(pk = verificar['id'])
        barbero = usuario.barberos.first()
        cita_barbero = barbero.cita_barbero.all()
        estados = Citas.ESTADOS


        contexto={
            'barbero':barbero,
            'cita_barbero' :cita_barbero,
            'estados' : estados,
            
        } 
        return render(request,'barberos/panel_barbero.html',contexto)
    except Usuarios.DoesNotExist:
        messages.warning(request,'❌ ERROR :No hay Datos Sobre Usuarios  Asociados')
    except Barberos.DoesNotExist:
        messages.warning(request,'❌ ERROR :No hay Datos Sobre Barberos Asociados')
    except CitaServicios.DoesNotExist:
        messages.warning(request,'❌ ERROR :No hay Datos Sobre Barberos Asociados')
    except Citas.DoesNotExist:
        messages.warning(request,'❌ ERROR :No hay Datos Sobre Barberos Asociados')
    return redirect('index')

def enviar_correo_html ( request,id_cliente ):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'B':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        cliente = Clientes.objects.get(pk = id_cliente)
        return render(request,'barberos/enviar_correo_html.html',{'cliente':cliente})
    except Clientes.DoesNotExist:
        messages.error(request, "❌ No hay Datos Existentes.")
        return redirect('panel_barbero')

def enviar_correo(request):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'B':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST' :
        asunto  =request.POST.get('asunto')
        mensaje =request.POST.get('mensaje')
        correo  =request.POST.get('correo') 
        try:
            send_mail(
                asunto,
                '',  # Aquí no va texto plano
                'santiagoholguin150@gmail.com',
                [correo],
                fail_silently=False,
                html_message=mensaje
            )
            messages.success(request, "✅ Correo enviado correctamente.")
        except Exception as e:
            messages.error(request, "❌ Error al enviar el correo.")
    return redirect('panel_barbero')

def actualizar_estado(request,id_cita):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'B':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        estado = request.POST.get('estado')
        try:
            cita = Citas.objects.get(pk = id_cita)
            cita.estado = estado
            cita.save()
        except Citas.DoesNotExist:
            messages.warning(request,'⚠️ WARNING : No Hay Datos Asociados')
    return redirect('panel_barbero')

#endregion


#region ADMIN PANEL
#incio

#
def admin_panel(request):
    verificar = request.session.get('logueado',False)
    if not verificar or  verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    citas=Citas.objects.order_by('-id')[:1]
    clientes=Clientes.objects.order_by('-id')[:1]
    barberos=Barberos.objects.order_by('-id')[:1]
    admin=Administradores.objects.order_by('-id')[:1]
    servicios=Servicios.objects.order_by('-id')[:1]
    productos=Productos.objects.order_by('-id')[:1]
    
    todas_citas = Citas.objects.all()
    todos_clientes = Clientes.objects.all()
    pagos=Pagos.objects.order_by('-id')[:1]
    contexto = {
        'citas ': citas,
        'barberos' :barberos,
        'servicios':servicios,
        'productos':productos,
        'pagos':pagos,
        'admins':admin,
        "clientes" : clientes,
        "todas_citas" : todas_citas,
        "todos_clientes" :todos_clientes
    }
    
    return render(request,'admin/inicio.html',contexto)

#region USUARIOS
def listar_usuarios(request):
    verificar = request.session.get('logueado',False)
    if not verificar or  verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    else:
        q = Usuarios.objects.all()
        barberos = Barberos.objects.all()
        ROLES = Usuarios.ROLES
        contexto = {
            'usuarios' : q,
            'roles' :ROLES,
            'barberos' :barberos
        }
        return render(request,'admin/usuarios/listar_usuarios.html',contexto)

def eliminar_usuario(request,id_usuario): # Inactiva el usuario 
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        usuario = Usuarios.objects.get(pk = id_usuario)
        if usuario.tipoUsuario != 'A' :
            usuario.foto.delete()
            usuario.delete()
            messages.success(request,' ✅ MENSAJES : Usuario eliminado correctamente  ')
            return redirect('listar_usuarios')
        else:
            messages.warning(request,'⚠️ WARNING : No Puedes Eliminar A Un Administrador')
            return redirect('listar_usuarios')
    except Usuarios.DoesNotExist:
        messages.error(request,' ❌ ERROR : No Hay Cuentas Sobre Usuarios Asociados')
    except Exception as e:
        messages.error(request,f'❌ ERROR : {e}')
    return redirect('listar_usuarios')
#endregion

#region SERVICIOS
def listar_servicios(request):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'A' :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        id=request.POST.get('id')
        try:
            servicio = Servicios.objects.get(pk = id)
            servicio.nombre = request.POST.get('nombre')
            servicio.precio = request.POST.get('precio')
            servicio.duracion = request.POST.get('duracion')
            servicio.descripcion = request.POST.get('descripcion')
            servicio.categoria = request.POST.get('categoria')
            servicio.img_url = request.POST.get('img_url') # El ID QUE TIENEN LAS IMAGENES DE PIXABY
            servicio.save()
            messages.success(request,'✅ MENSAJE : Servicio Actualizado Correctamente')
            return redirect('listar_servicios')
        except Servicios.DoesNotExist:
            messages.success(request,'❌ ERROR : No hay Servicios Asociados')
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
        return redirect('listar_servicios')
    else:
        servicios = Servicios.objects.all()
        categorias = Servicios.CATEGORIAS
        contexto ={
            'servicios' : servicios,
            'categorias' : categorias,
        }
        return render(request,'admin/servicios/listar_servicios.html',contexto)

def nuevo_servicio(request):
    verificar = request.session.get('logueado',False)
    if not verificar or  verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        try:
            nuevo = Servicios(
                nombre = request.POST.get('nombre'),
                precio = request.POST.get('precio'),
            )
            nuevo.save()
            messages.success(request,' ✅ MENSAJE :  Servicio Agregado Con Exito')
            return redirect('listar_servicios')
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
            return redirect('listar_servicios')
    else:
        return redirect('listar_servicios')

def eliminar_servicio(request,id_servicio):
    verificar = request.session.get('logueado',{})
    if verificar.get('rol') != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        servicio = Servicios.objects.get(pk = id_servicio)
        servicio.delete()
        messages.success(request,' ✅ MENSAJE : Servicio Eliminado Correctamente')
        return redirect('listar_servicios')
    except Servicios.DoesNotExist:
        messages.error(request,' ❌ ERROR : No Hay Datos Sobre Servicios Asociados')
    except Exception as e:
        messages.error(request,f' ❌ ERROR : {e}')
    return redirect('listar_servicios')

#endregion

#region BARBEROS
def detalles_barberos(request,id_barbero):
    verificar = request.session.get('logueado',False)
    if  not verificar or verificar['rol'] != 'A' :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('login')
    else:
        try:
            barbero = Barberos.objects.get(pk = id_barbero)
            dias = Barberos.DIAS
            
            if request.method == 'POST' :
                horario_trabajo =  request.POST.get('horario_trabajo')
                hora_inicio = request.POST.get('hora_inicio')
                hora_final =  request.POST.get('hora_final')
                barbero.horario_trabajo = horario_trabajo
                barbero.hora_inicio = hora_inicio
                barbero.hora_final = hora_final
                messages.success(request,f'Se Asigno El Horario Correctamente a {barbero.usuario_barbero.nombre_completo}')
                barbero.save()
                return redirect('detalles_barberos',id_barbero=id_barbero)
            cita_barberos = Citas.objects.filter(barbero=id_barbero)
            contador={}
            for cita in cita_barberos:
                cliente = cita.cliente
                if cliente in contador:
                    contador[cliente] += 1
                else:
                    contador[cliente] =1
            clientes_recurrentes = [cliente for cliente, cantidad in contador.items() if cantidad > 1]

            contexto = {
                'barbero' : barbero,
                'dias' :dias,
                'cita_barberos' : cita_barberos,
                'clientes_recurrentes' :clientes_recurrentes,
            }
            return render(request,'admin/usuarios/detalles_barberos.html',contexto)
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
            return redirect('listar_usuarios')

#endregion

#region CITAS
def listar_citas(request):
    verificar = request.session.get('logueado',False)
    if not verificar  or verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    q = Citas.objects.all()
    contexto = {
        'citas' : q,
    }
    return render(request,'admin/citas/listar_citas.html',contexto)
#endregion

#region INVENTARIO
def inventario(request):
    verificar = request.session.get('logueado',{})
    if  verificar.get('rol') != 'A'  :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            producto = Inventarios.objects.get(pk = id)
            producto.stock = request.POST.get('stock')
            producto.save()
            messages.success(request,' ✅ MENSAJE : Producto Actualizado Con Exito ')
            return redirect('inventario')
        except Inventarios.DoesNotExist:
            messages.success(request,'❌ ERROR : No Hay Datos Sobre Productos Asociados ')
        except Exception as e:
            messages.success(request,f'❌ ERROR :{e}')
        return redirect('inventario')
    inventario = Inventarios.objects.all()
    contexto={
        'inventario' : inventario
    }
    return render(request,'admin/inventario.html',contexto)

#endregion

#region PRODUCTOS

def listar_productos(request):
    verificar = request.session.get('logueado',False)
    if not verificar or  verificar['rol'] != 'A'  :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST' :
        try:
            id = request.POST.get('id')
            producto = Productos.objects.get(pk = id)
            producto.nombre = request.POST.get('nombre')
            producto.precio = request.POST.get('precio')
            producto.descripcion = request.POST.get('descripcion')
            producto.categoria = request.POST.get('categoria')
            producto.img_url = request.POST.get('img_url') # El ID QUE TIENEN LAS IMAGENES DE PIXABY
            producto.save()
            messages.success(request,' ✅ MENSAJE : Producto Actualizado Con Exito ')
            return redirect('listar_productos')
        except Productos.DoesNotExist:
            messages.success(request,'❌ ERROR : No Hay Datos Sobre Productos Asociados ')
        except Exception as e:
            messages.success(request,f'❌ ERROR :{e}')
        return redirect('listar_productos')
    productos = Productos.objects.all()
    categorias = Productos.CATEGORIAS
    contexto = {
        'productos' : productos,
        'categorias' :categorias
    }
    return render(request,'admin/productos/listar_productos.html',contexto)

def nuevo_producto(request):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'A' :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        try:
            producto = Productos(
                nombre = request.POST.get('nombre'),
                precio = request.POST.get('precio'),
            )
            producto.save()
            add_inventario = Inventarios(
                producto = producto,
                stock = 0
            )
            add_inventario.save()
            messages.success(request,' ✅ MENSAJE : Producto Agregado Con Exito')
            return redirect('listar_productos')
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
            return redirect('listar_productos')
    else:
        return redirect('listar_productos')

def detalle_producto(request,id_producto):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    inventario_producto = Inventarios.objects.get(pk = id_producto)
    try:
        if request.method =='POST':
            inventario_producto.stock = request.POST.get('stock')
            inventario_producto.save()
            messages.success(request,'Stock Actualizado Con Exito')
            return redirect('inventario')
        contexto ={
            "producto" : inventario_producto
        }
        return render(request,'admin/productos/detalle_productos.html',contexto)
    except Inventarios.DoesNotExist:
            messages.error(request,'❌ ERROR :No Hay Datos Sobre Productos Asociados')
    except Exception as e:
        messages.error(request,f'❌ ERROR : {e}')
    return redirect('listar_productos')

def eliminar_producto(request,id_producto):
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'A':
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        producto = Productos.objects.get(pk = id_producto)
        producto.delete()
        messages.success(request,' ✅ MENSAJE : Producto Eliminado Correctamente')
        return redirect('listar_productos')
    except Productos.DoesNotExist:
        messages.error(request,'❌ ERROR :No Hay Datos Sobre Productos Asociados')
    except Exception as e:
        messages.error(request,f'❌ ERROR : {e}')
    return redirect('listar_productos')

#endregion

#region PAGOS
def listar_pagos(request):
    verificar = request.session.get('logueado',False)
    if not verificar or  verificar['rol'] != 'A'  :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('index')
    try:
        pagos = Pagos.objects.all()
        return render (request,'admin/listar_pagos.html',{'pagos' : pagos})
    except Exception as e:
        messages.error(request,f'{e}')
        return redirect('index')


#endregion

#region PANEL DE SESION
#Autenticar y redireccionar usuarios
def login(request):
    if request.method == 'POST':
        #Obtener los valores ingresados en el HTML
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Se Obtiene y se compara el email del modelo Usuarios con los datos ingresados en el HTML
            consulta = Usuarios.objects.get(email=email)
            
            #Se compara la contraseña ingresada en el HTML con el hash guarado en la base de datos
            if verify_password(password,consulta.password):
                #Se crea la sesion con el nombre logueado , y se guardan los datos del usuario 
                request.session['logueado']={
                    "id":consulta.id,
                    "email" :consulta.email,
                    "nombre" : consulta.nombre_completo,
                    "username" : consulta.username,
                    "foto" : consulta.foto.url,
                    "rol" : consulta.tipoUsuario
                }
                verificar = request.session.get('logueado',False)
                nombre = verificar['nombre']
                # Si el nombre esta vacio se asigna explorador para que en el envio del correo no quede vacio ni en las tablas
                if nombre  == None :
                    nombre = 'Explorador'
                # segun el rol que inicia sesion se muestra un mensaje si es admin , se redirecciona al panel del administrador
                if verificar['rol'] == 'A':
                    messages.success(request,f'✅ MENSAJE : Inicio de Sesion Exitoso , Hola de nuevo  Admin / {nombre}')
                    return redirect('admin_panel')
                elif verificar['rol'] == 'B':
                    messages.success(request,f'✅ MENSAJE : Inicio de Sesion Exitoso , Hola de nuevo  Barbero / {nombre}')
                    return redirect('panel_barbero')
                else:
                    messages.success(request,f'✅ MENSAJE : Inicio de Sesion Exitoso , Hola de nuevo  Colega  / {nombre}')
                    return redirect('index')
            #Si la contraseña no concide con el hash guardado
            else:
                messages.error(request,'No existe el usuario')
        #Si el usuario no existe en la base de datos
        except Usuarios.DoesNotExist :
            messages.error(request,'❌ ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        # si el usuario no existe en la base de datos 
        except NameError :
            messages.error(request,'❌ ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        # Errores internos
        except Exception as e :
            messages.error(request,f'❌ ERROR :{e}')
            request.session['logueado'] = None
        return redirect('login')
    else:
        # si el usuario ya incio sesion , no podra devolverse a esta vista , debera cerrar sesion 
        verificar = request.session.get('logueado',False)
        if verificar:
            messages.info(request , 'ℹ️ INFO : Ya Iniciaste Sesion , No Puedes Hacerlo Otra Vez')
            return redirect('index')
        return render(request,'panel/login.html')

#Destruir sesion
def logout(request):
    #si no esta logueado mostrar error y redirecciona al login
    verificar = request.session.get('logueado',False)
    if not verificar  :
        messages.warning(request,'⚠️ WARNING : No Tienes Permitido Hacer Esto')
        return redirect('login')
    #si ya inicio sesion podra destuir la sesion 
    else:
        try:
            del request.session['logueado']
            messages.success(request,'✅ MENSAJE : Se Cerro La Sesion Correctamente')
            return redirect('index')
        # mas que todo este error es por si falla la conexion 
        except Exception as e:
            messages.info(request,f'❌ ERROR : Ocurrio Un Error Inesperado Intente Nuevamente Detalles: {e}')
        return redirect('index')

#REGISTRAR USUARIOS
def register(request):
    """
    Función para registrar nuevos usuarios en la plataforma (Clientes, Barberos y Administradores).

    - Se utiliza la misma vista para procesar todos los registros, evitando crear múltiples funciones de registro.
    - Los Clientes pueden registrarse desde el login/index sin necesidad de elegir un rol.
    - Solo los Administradores pueden crear cuentas de Barberos y otros Administradores desde el panel de administración.
    
    - El formulario de registro es simple y solo requiere correo y contraseña, pero en el panel de administración se muestra una opción adicional para seleccionar el rol.
    
    - Se asegura que los usuarios con sesión activa no puedan acceder al formulario de registro para evitar duplicados o cambios no autorizados.
"""
    verificar = request.session.get('logueado',False)
    if verificar and verificar.get('rol') == 'A':
        if request.method == 'POST' :
            foto = request.FILES.get('foto') # Estas opcion esta oculta en el html para todos los roles  pero la pongo para que se pueda procesar la foto decir si es se sube o no 
            rol = request.POST.get('rol') # lo mismo pasa con el rol pero esta opcion si la muestro en el Panel del adminstrador , ya que solo el admin puede crear cuentas con rol  Admin y Barbero (Cuentas con rol Cliente no puede creear)
            password= request.POST.get('password') # Se optiene el password del html
            encriptada = hash_password(password) # se encripta la password del html 
            email = request.POST.get('email')
            if not rol:
                messages.warning(request,' ⚠️ WARNING : Debes Seleccionar Un Rol ')
                return redirect('listar_usuarios')
            # Try para procesar el guardado de usuario en la BD
            try:
                validate_email(email) # Valida que el correo sea tipo email antes de validar
                # Se asigna la variable que guardara el usuario 
                q = Usuarios(
                email = request.POST.get('email'), # se obtine el email del formulario (en este caso esta funcion esta para funcionar atravves de una url asiganada en un action de un html)
                password = encriptada,
                nombre_completo = 'Explorador',
                tipoUsuario = rol
                )
                
                q.save() # se guara el usuario que esta en la variable q en la BD si todo esta bien 
                # SI se sube foto se procesa y se vuelve redonda y si no se sube predeterminada
                if foto:
                    foto_procesada = hacer_imagen_redonda(foto)
                    q.foto.save(f"perfil_{q.email}.png", foto_procesada)
                else:
                    # Si no subió foto, usar la predeterminada y hacerla redonda
                    default_path = os.path.join(settings.MEDIA_ROOT, 'fotos/predeterminado.png')
                    with open(default_path, 'rb') as default_image:
                        foto_procesada = hacer_imagen_redonda(default_image)
                        q.foto.save(f"perfil_{q.email}.png", foto_procesada)  # Guarda la imagen


                # Si se registra como barbero hacer la conexion con la clase Barberos con la instancia del usuario q
                if rol == 'B' :
                    # se asigna la variable para guarar el barbero con la instancia del usuario que se acaba de crear si el rol es barbero 
                    admin_email = verificar.get('email')
                    creador = Usuarios.objects.get(email=admin_email)
                    new_barber = Barberos(
                        usuario_barbero = q,
                        admin_creador = creador
                    )
                    messages.success(request,"Barbero Agregado Correctamente")
                    new_barber.save()
                # Si se registra como administrador hacer la conexion a la clase Adminustrador con la instancia del usuario q que se acabo de creear
                elif rol == 'A':
                    # se asigna la variable para guarar el admin con la instancia del usuario que se acaba de crear si el rol es admin 
                    new_admin = Administradores(
                        usuario_admin = q
                    )
                    messages.success(request,"Administrador Agregado Correctamente")
                    new_admin.save()
                # Envio de correo si el correo es gmail , si no es gmail o el correo no existe , de igual forma se crea el usuario
                try:
                    html_message = f'''
                    <p>👋 Hola, <strong>Colega </strong> Listo para un nuevo estilo !</p>

                    <p>Tu cuenta como <strong> {q.get_tipoUsuario_display()} </strong> ha sido creada exitosamente en nuestra plataforma. 🎉</p>

                    <p>🔹 <strong>Correo electrónico:</strong> {q.email}</p>

                    <p>Para acceder a tu cuenta, haz clic en el siguiente enlace:</p>

                    <p>➡️ <a href="http://127.0.0.1:8000/" style="color: #007bff; text-decoration: none; font-weight: bold;">Iniciar sesión en Ziara App</a></p>

                    <p>¡Bienvenido a Ziara! Estamos encantados de tenerte con nosotros. 💈✨</p>
                    '''

                    send_mail(
                        'Registro de Usuario en Educalab',
                        "",
                        'santiagoholguin150@gmail.com',
                        [f'{q.email}'],
                        fail_silently=False, html_message = html_message
                    )
                    
                    # Condicionales para cada rol evitar mensajes incoherentes o inapropiados o redirecciones no debibas 
                    messages.success(request, " ✅ MENSAJE :  Correo enviado !!")
                except Exception as error :
                    messages.error(request, f" ❌ ERROR : NO SE PUEDE ENVIAR CORREO ")
                return redirect('listar_usuarios')

            except ValidationError :
                messages.warning(request, '⚠️ WARNING : Escriba Un Correo Con La Estructura Adecuada  .  joe_doe@example.com ') # Si el correo no es tipo email muestra el mensaje
            except IntegrityError :
                messages.error(request, '❌ ERROR : El correo ya esta en uso ') # Si el correo ya existe mostrar esta excepcion 
            except Exception as error :
                messages.error(request, f" ❌ ERROR: No Se puede crear la cuenta : {error}")
            return redirect('listar_usuarios')

        # si por alguna razon se pone la ruta register que es la que esta en url esta protegida para que aparezca el index
        else:
            return render (request,'index.html')
        """
        Como solo quise usar esta vista para registrar clientes , admins y barbers pues hice un condicional que me dijiera si habia una sesion y si en esa siosn el rol era admin pues ejectuara el codigo de arriba y si no pues ejectutara este , al principio lo tenia junto todo sin el condicional , pero tenia problemas con el manejo de las sesiones y la solucion era hacer otra vista para registrar clientes, ya que ese era el inconveniente , para poder registrarlo sin el condicional me tocaba mostrar el div que contiene el rol y poner display none , el problema es que cualquiera podria entrar en la consola del navegador y cambiarse el rol para admin o barber y crearse la cuenta o incluso poner el input en display pero ya NO NONE , grave problema entonces mejor decidi separar las dos logicas diciendo que si hay sesion y es admin , la logica para registrar en el formulario trae el aatributo rol es decir esta presente en el formulario , pero en else ( que en este caso seria para el cliente este formulario se maneja en los archivos base y panel base ) ya ese atributo desaparece asi eliminamos del archivo base(exporta para el index ) y panel base (exporta para login) en el formulario el div que contiene el rol y solo dejamos la foto 
        --------------------------------------------------------------------------------------------------------------
        
        Lógica para diferenciar los registros de Administradores/Barberos y Clientes:

        - Si hay una sesión activa y el usuario es Administrador, el formulario de registro incluye la opción para asignar un rol. Esto permite registrar Barberos y Administradores.
        - Si no hay sesión activa o el usuario no es Administrador, solo se permite el registro de Clientes sin la opción de elegir un rol.
        - Se implementa esta lógica para evitar que cualquier usuario modifique el formulario desde la consola del navegador y se registre con un rol no autorizado.
        - De esta forma, los formularios en los archivos base y panel base solo incluyen el campo de foto para Clientes y eliminan la opción de rol.
"""
    else:
        if request.method == 'POST' :
            foto = request.FILES.get('foto') # Estas opcion esta oculta en el html para todos los roles  pero la pongo para que se pueda procesar la foto decir si es se sube o no 
            password= request.POST.get('password') # Se optiene el password del html
            encriptada = hash_password(password) # se encripta la password del html 
            email = request.POST.get('email')
            # Try para procesar el guardado de usuario en la BD
            try:
                validate_email(email)
                # Se asigna la variable que guardara el usuario 
                q = Usuarios(
                email = email, # se obtine el email del formulario (en este caso esta funcion esta para funcionar atravves de una url asiganada en un action de un html)
                password = encriptada,
                nombre_completo = 'Explorador',
                )
                q.save() # se guara el usuario que esta en la variable q en la BD si todo esta bien 
                messages.success(request,"Cuenta Agregada Correctamente")
                # SI se sube foto se procesa y se vuelve redonda y si no se sube predeterminada
                if q.tipoUsuario == 'C' :
                    nuevo_cliente = Clientes(
                        usuario_cliente = q
                    )
                    nuevo_cliente.save()
                if foto:
                    foto_procesada = hacer_imagen_redonda(foto)
                    q.foto.save(f"perfil_{q.email}.png", foto_procesada)
                else:
                    # Si no subió foto, usar la predeterminada y hacerla redonda
                    default_path = os.path.join(settings.MEDIA_ROOT, 'fotos/predeterminado.png')
                    with open(default_path, 'rb') as default_image:
                        foto_procesada = hacer_imagen_redonda(default_image)
                        q.foto.save(f"perfil_{q.email}.png", foto_procesada)  # Guarda la imagen
                # Envio de correo si el correo es gmail , si no es gmail o el correo no existe , de igual forma se crea el usuario
                try:
                    html_message = f'''
                    <p>👋 Hola, <strong>Colega </strong> Listo para un nuevo estilo !</p>

                    <p>Tu cuenta como <strong> {q.get_tipoUsuario_display()} </strong> ha sido creada exitosamente en nuestra plataforma. 🎉</p>

                    <p>🔹 <strong>Correo electrónico:</strong> {q.email}</p>

                    <p>Para acceder a tu cuenta, haz clic en el siguiente enlace:</p>

                    <p>➡️ <a href="http://127.0.0.1:8000/" style="color: #007bff; text-decoration: none; font-weight: bold;">Iniciar sesión en Ziara App</a></p>

                    <p>¡Bienvenido a Ziara! Estamos encantados de tenerte con nosotros. 💈✨</p>
                    '''

                    send_mail(
                        'Registro de Usuario en Educalab',
                        "",
                        'santiagoholguin150@gmail.com',
                        [f'{q.email}'],
                        fail_silently=False, html_message = html_message
                    )
                    
                    # Condicionales para cada rol evitar mensajes incoherentes o inapropiados o redirecciones no debibas 

                    messages.success(request, "Correo enviado !!")
                except Exception as error :
                    messages.error(request, f"No se pudo enviar el correo: {error}")
                return redirect('login')
            
            except ValidationError :
                messages.warning(request, ' ⚠️ WARNING : Escriba Un Correo Con La Estructura Adecuada . joe_doe@example.com ')
            except IntegrityError :
                messages.info(request, ' ℹ️ INFO : Este Correo No Esta Disponible . ')
            except Exception as error :
                messages.error(request, f" ❌ ERROR: No Se puede crear la cuenta : {error}rrr")
            return redirect('login')
        # si por alguna razon se pone la ruta register que es la que esta en url esta protegida para que aparezca el index
        else:
            return render (request,'index.html')

#PERFIL
def ver_perfil(request,id_usuario):
    verficar = request.session.get('logueado',False)
    if not verficar:
        messages.error(request,'Debes Iniciar Sesion')
        return redirect('index')
    elif verficar['id'] != id_usuario:
        messages.warning(request,'ERROR : Detente no puedes hacer esto')
        return redirect('index')
    elif verficar['rol'] == 'A':
        plantila_usada = "admin/admin_base.html"
    else:
        plantila_usada = "base.html"
    if request.method == 'POST' :
        usuario = Usuarios.objects.get(pk = id_usuario)
        barbero = usuario.barberos.first()
        especialidad = request.POST.get('especialidad')
        experiencia = request.POST.get('experiencia')
        email= request.POST.get('email')
        name = request.POST.get('name')
        username = request.POST.get('username')
        tel = request.POST.get('tel')
        f_nacimiento = request.POST.get('f_nacimiento')
        foto_subida = request.FILES.get('foto')
        try:
            if barbero:
                barbero.especialidad = especialidad
                barbero.experiencia = experiencia
                barbero.save()
            usuario.email = email
            usuario.nombre_completo = name
            usuario.username = username
            usuario.telefono = tel
            usuario.f_nacimiento = f_nacimiento
            if foto_subida:
                try:
                    validate_image_file_extension(foto_subida)
                    #Se hace la foto redonda para evitar que suban fotos de cualquier tamaño
                    foto_procesada = hacer_imagen_redonda(foto_subida)
                    
                    # Borrar la imagen anterior para evitar archivos basura
                    if usuario.foto and usuario.foto.name:
                        usuario.foto.delete(save=False)

                    # 🔵 Generar un nombre seguro para el archivo Este paso se puede omitir por nombre_archivo = f"{usuarioLogeado.id}.png" si no queremos usar las librerias
                    user_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', usuario.username)  # Limpia caracteres especiales
                    nombre_archivo = f"{user_clean}_{uuid.uuid4().hex[:8]}.png"
                    usuario.foto.save(nombre_archivo, foto_procesada, save=True) # ! Esto sobrescribe la imagen que ya tiene guardada en media 
                    usuario.save() # * Guarda los cambios en la BD
                    messages.info(request,'ℹ️ INFO : Tu Informacion y Foto se ha actualizado correctamente. Por favor, inicia sesión nuevamente.')
                    del request.session['logueado']
                except ValidationError : 
                    messages.warning(request,'⚠️ WARNING : Solo puedes subir imágenes en formato PNG , JPG Ó GIF')
                    return redirect(request.META.get('HTTP_REFERER', 'index'))
            else:   
                usuario.save() # * Guarda los cambios en la BD
                messages.info(request,'ℹ️ INFO : Tu información se ha actualizado correctamente.')
                return redirect(request.META.get('HTTP_REFERER', 'index'))
            return redirect('index')
        except Exception as e:
            messages.error(request,f'{e}')
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    else:
        usuario = Usuarios.objects.get(pk = id_usuario)
        contexto ={
            'plantilla_usada' : plantila_usada,
            'usuario':usuario,
        }
        return render(request,'panel/ver_perfil.html',contexto)

# Recuperacion de clave por token 
def recueperar_password(request):
    verificar = request.session.get('logueado',False)
    if not verificar:
        messages.error(request,'Permiso Denegado')
        return redirect('index')
    if request.method == 'POST' :
        email = request.POST.get('email')
        try:
            q = Usuarios.objects.get(email=email)
        except Usuarios.DoesNotExist:
            messages.info(request,'Se ha enviado un correo a su cuenta registrada')
            return redirect('recuperar_password')
        from random import randint
        token = randint(10000,999999)
        q.token_recuperar_clave = token
        q.save()
        if q.username == '':
            q.username = 'Invitado'
        try:
            html_message = f'''
            <p><strong> {q.username} </strong>, hemos recibido una solicitud para restablecer tu contraseña.</p>

            <p>Por favor, usa el siguiente token de seguridad para completar el proceso:</p>

            <p><strong>TOKEN:</strong> {token}</p>

            <p>Para continuar, haz clic en el siguiente enlace e ingresa el token:</p>

            <p>
                ➡️ <a href="http://127.0.0.1:8000/verificacion_token_recuperar_password/?email=True&correo={q.email}" 
                style="color: #007bff; text-decoration: none; font-weight: bold;">
                Recuperar contraseña en Ziara</a>
            </p>

            <p>Si no solicitaste este cambio, ignora este mensaje.</p>

            <p>💈 <strong>El equipo de Ziara</strong></p>
            '''
            send_mail(
                    'Movimientos en su cuenta Ziara',
                    "",
                    'santiagoholguin150@gmail.com',
                    [f'{q.email}'],
                    fail_silently=False, html_message = html_message
                )
            messages.success(request, "Correo enviado !!")
            return redirect('index')
        except Exception as e :
            messages.error(request, f'{e}')
            return redirect('recuperar_password')
    else:
        return render(request,'panel/recuperar_clave.html')

#Verificacion de token 
def verificacion_token_recuperar_password(request):
    verificar = request.session.get('logueado',False)
    if not verificar:
        messages.error(request,'Permiso Denegado')
        return redirect('index')
    if request.method == 'POST':
        token = request.POST.get('token')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        try:
            q = Usuarios.objects.get(email=email)
            if q.token_recuperar_clave == token:
                if password == password2:
                    q.token_recuperar_clave = ''
                    q.password = hash_password(password)
                    q.save()
                    messages.success(request, "Contraseña recuperada correctamente!")
                    return redirect("index")
                else:
                    messages.warning(request,'Las contraseñas no conciden')
            else:
                    messages.warning(request,'No concide el token de seguridad')
        except Usuarios.DoesNotExist:
                messages.warning(request,'No hay Cuentas Asociadas')
        except Exception as e:
            messages.warning(request,'No hay Cuentas Asociadas')
        return redirect('verificacion_token_recuperar_password')
    else:
        correo = request.GET.get('correo')
        contexto ={
            'correo' :correo
        }
        return render(request,'panel/verificacion_token_recuperar_password.html',contexto)

#'('email', 'password', 'nombre_completo', 'telefono', 'f_nacimiento', 'foto', 'tipoUsuario', )'
#endregion

#region NOTIFICACIONES

#PARA EL PANEL ADMIN
def ultimos_datos_admin(request):
    notificaciones = []
    verificar = request.session.get('logueado',False)
    if not verificar :
        messages.info(request,'❌ERROR : Debes iniciar sesion primero')
        return redirect('index')
    elif verificar['rol'] != 'A':
        messages.info(request,'❌ERROR : No tienes los permisos necesarios')
        return redirect('index')
    usuarios = Usuarios.objects.order_by('-id')[:1]
    servicios = Servicios.objects.order_by('-id')[:1]
    citas = Citas.objects.order_by('-id')[:1]
    for usuario in usuarios:
        notificaciones.append(f'{usuario.nombre_completo} Se ha registrado')
    for servicio in servicios:
        notificaciones.append(f'El servicio {servicio.nombre} fue añadio  ')
    for cita in citas:
        notificaciones.append(f'{cita.cliente.usuario_cliente.nombre_completo} agendo una cita  ')
    return JsonResponse({'notificaciones':notificaciones})


#endregion

#region Realizar Venta
def confirmar_reserva(request): # html para seleccioanar barbero , fecha y hora si es un servicio y tambien para pagar los productos que seleccionemos 
    verificar = request.session.get('logueado',False)
    if not verificar or verificar['rol'] != 'C':
        messages.error(request,'Permiso Denegado')
        return redirect('index')
    carrito_id = request.session.get('carrito_servicios', [])
    carrito_producto_id = request.session.get('carrito_productos', [])
    
    carrito_servicios = Servicios.objects.filter(id__in=carrito_id)
    carrito_productos = Productos.objects.filter(id__in=carrito_producto_id)
    barberos=Barberos.objects.all()
    
    total = sum(s.precio for s in carrito_servicios) + sum(p.precio for p in carrito_productos)
    suma = len(carrito_productos) + len(carrito_servicios)
    
    return render(request, 'ventas/confirmar_reserva.html', {
        'carrito_servicios': carrito_servicios,
        'carrito_productos': carrito_productos,
        'total': total,
        'suma' : suma,
        'barberos' : barberos
    })


def realizar_compra(request):
    verificar = request.session.get('logueado', False)
    verificar_carrito = request.session.get('carrito_servicios', [])
    verificar_carrito_productos = request.session.get('carrito_productos', [])

    if not verificar or verificar['rol'] != 'C':
        messages.error(request, 'Permiso Denegado')
        return redirect('index')

    if request.method == 'POST':
        try:
            usuario = Usuarios.objects.get(pk=verificar['id'])
            cliente = Clientes.objects.get(usuario_cliente=usuario)

            # Si hay servicios en el carrito
            if verificar_carrito:
                primer_servicio_id = verificar_carrito[0]  # Usamos el primer servicio como referencia

                fecha_str = request.POST.get('fecha')
                hora_str = request.POST.get('hora')
                barbero_id = request.POST.get('barbero')

                if not fecha_str or not hora_str or not barbero_id:
                    messages.error(request, 'Por favor completa la fecha, hora y barbero.')
                    return redirect('confirmar_reserva')

                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                hora = datetime.strptime(hora_str, '%H:%M').time()
                barbero = Barberos.objects.get(id=barbero_id)

                # Creamos la cita principal
                cita = Citas.objects.create(
                    cliente=cliente,
                    hora=hora,
                    fecha=fecha,
                    estado='PRO',
                    barbero=barbero
                )

                # Asociamos todos los servicios seleccionados a la cita
                for servicio_id in verificar_carrito:
                    servicio = Servicios.objects.get(id=servicio_id)
                    CitaServicios.objects.create(cita=cita, servicio=servicio)

                # Calculamos el total de los servicios
                total_servicios = sum(Servicios.objects.get(id=s).precio for s in verificar_carrito)
            else:
                total_servicios = 0  # Si no hay servicios, el total de servicios es 0

            # Calculamos el total de los productos
            total_productos = sum(Productos.objects.get(id=p).precio for p in verificar_carrito_productos)

            # Total general
            total = total_servicios + total_productos

            # Creamos el pago asociado a la cita (si hay cita)
            pago = Pagos.objects.create(
                cliente=cliente,
                monto_total=total,
                cita=cita if verificar_carrito else None  # Asocia la cita si hay
            )

            # Si hay productos, los procesamos
            for id_producto in verificar_carrito_productos:
                producto = Productos.objects.get(id=id_producto)
                inventario = Inventarios.objects.get(producto=producto)

                if inventario.stock > 0:
                    inventario.stock -= 1
                    inventario.save()

                    ProductosComprados.objects.create(
                        pago=pago,
                        producto=producto,
                    )
                else:
                    messages.error(request, f'Producto sin stock: {producto.nombre}')
                    return redirect('confirmar_reserva')

            # Limpiamos el carrito
            request.session['carrito_servicios'] = []
            request.session['carrito_productos'] = []

            messages.success(request, '✅ MENSAJE: Compra Realizada Con Éxito')
            return redirect('index')

        except Exception as e:
            messages.warning(request, f'❌ ERROR al procesar la compra: {e}')
            return redirect('confirmar_reserva')

    return redirect('confirmar_reserva')

def historial_pagos(request):
    verificiar = request.session.get('logueado',False)
    if not verificiar:
        messages.error(request,'No tienes Permitido hacer esto')
        return redirect('index')
    try:
        usuario = Usuarios.objects.get(pk = verificiar['id'])
        cliente = Clientes.objects.get(usuario_cliente = usuario)
        pagos = cliente.pagos.all()
        
        return render (request,'clientes/historial_pagos.html',{'pagos' : pagos})
    except Exception as e:
        messages.error(request,f'{e}')
        return redirect('index')
#endregion

#region DjangoRestFramework
from .serializer import *

from rest_framework import viewsets

#get ,post,putch,delete,put
class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.all()
    serializer_class = ServiciosSerializer
#endregion