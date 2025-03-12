from django.shortcuts import render,redirect
from django.contrib import messages 
from .models import * # Importacion de todos los modelos en models.py
from .utils import * # Importacion de la funcion de incriptacion y verificacion del archivo utils.py

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


# Create your views here.

def index(request):
    verificar = request.session.get('logueado',False)
    if verificar == False:
        messages.warning(request,'ERROR : Debes Iniciar Sesion Primero ')
        return redirect('login')
    return render(request,'index.html')


def admin_panel(request):
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'ERROR : Debes Iniciar Sesion Primero ')
        return redirect('login')
    elif not verificar['rol'] == 'A':
        messages.warning(request,'ERROR : NO TIENES LOS PERMISOS NECESARIOS 🚫 ')
        return redirect('index')
    return render(request,'admin/admin_base.html')




#region PANEL DE SESION
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
                    "foto" : consulta.foto.url,
                    "rol" : consulta.tipoUsuario
                }
                verificar = request.session.get('logueado',False)
                nombre = verificar['nombre']
                
                if verificar['rol'] == 'A':
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Admin / {nombre}')
                    return redirect('admin_panel')
                elif verificar['rol'] == 'B':
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Barbero / {nombre}')
                    return redirect('index')
                else:
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Barbero / {nombre}')
                    return redirect('index')
            #Si la contraseña no concide con el hash guardado
            else:
                messages.error(request,'No existe el usuario')
        except Usuarios.DoesNotExist :
            messages.error(request,'ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        except NameError :
            messages.error(request,'ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        except Exception as e :
            messages.error(request,f'ERROR :{e}')
            request.session['logueado'] = None
        return redirect('login')
    else:
        verificar = request.session.get('logueado',False)
        if verificar:
            messages.error(request ,'Ya Iniciaste Sesion ')
            return redirect('index')
        return render(request,'panel/login.html')

def logout(request):
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'ERROR : Lo Siento Debes Iniciar Sesion Primero')
        return redirect('login')
    else:
        try:
            del request.session['logueado']
            messages.success(request,'Se Cerro La Sesion Correctamente')
            return redirect('login')
        except Exception as e:
            messages.info(request,f'Ocurrio Un Error Inesperado Intente Nuevamente Detalles: {e}')
        return redirect('index')

#'('email', 'password', 'nombre_completo', 'telefono', 'f_nacimiento', 'foto', 'tipoUsuario', )'
#endregion