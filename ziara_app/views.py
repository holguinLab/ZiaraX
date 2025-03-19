# Importacion de librerias
from django.shortcuts import render,redirect
from django.contrib import messages 
from .models import * # Importacion de todos los modelos en models.py
from .utils import * # Importacion de la funcion de incriptacion y verificacion del archivo utils.py
from django.db import IntegrityError

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

def index(request):
    return render(request,'index.html')

#region PROCESO DE IMAGENES
def hacer_imagen_redonda(imagen, tamaño=(150, 150)):
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

#region ADMIN PANEL
def admin_panel(request):
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'ERROR : Debes Iniciar Sesion Primero ')
        return redirect('login')
    elif not verificar['rol'] == 'A':
        messages.warning(request,'ERROR : NO TIENES LOS PERMISOS NECESARIOS 🚫 ')
        return redirect('index')
    return render(request,'admin/inicio.html')



#region CRUD USUARIOS
def listar_usuarios(request):
    pass 

def listar_usuarios(request):
    verificar = request.session.get('logueado',False)
    if not  verificar   :
        messages.info(request,'Debes Iniciar Sesion Primero')
        return redirect('index')
    elif not verificar['rol'] == 'A':
        messages.warning(request,'Permiso denegado')
        return redirect('index')
    else:
        q = Usuarios.objects.all()
        contexto = {
            'usuarios' : q
        }
        return render(request,'admin/usuarios/listar_usuarios.html',contexto)





#endregion

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
                    "username" : consulta.username,
                    "foto" : consulta.foto.url,
                    "rol" : consulta.tipoUsuario
                }
                verificar = request.session.get('logueado',False)
                nombre = verificar['nombre']
                if nombre  == None :
                    nombre = 'Explorador'
                if verificar['rol'] == 'A':
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Admin / {nombre}')
                    return redirect('admin_panel')
                elif verificar['rol'] == 'B':
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Barbero / {nombre}')
                    return redirect('index')
                else:
                    messages.success(request,f'Inicio de Sesion Exitoso , Hola de nuevo  Colega  / {nombre}')
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
            return redirect('index')
        except Exception as e:
            messages.info(request,f'Ocurrio Un Error Inesperado Intente Nuevamente Detalles: {e}')
        return redirect('index')

def register(request):
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'Debes iniciar sesion primero')
        return redirect('login')
    else:
        if request.method == 'POST' :
            foto = request.FILES.get('foto')
            password= request.POST.get('password')
            encriptada = hash_password(password)
            try:
                q = Usuarios(
                email = request.POST.get('email'),
                password = encriptada,
                nombre_completo = 'Explorador'
                ) 
                q.save()
                messages.success(request,"Usuario Agregado Correctamente")
                if foto:
                    foto_procesada = hacer_imagen_redonda(foto)
                    q.foto.save(f"perfil_{q.email}.png", foto_procesada)
                else:
                    # Si no subió foto, usar la predeterminada y hacerla redonda
                    default_path = os.path.join(settings.MEDIA_ROOT, 'fotos/predeterminado.png')
                    with open(default_path, 'rb') as default_image:
                        foto_procesada = hacer_imagen_redonda(default_image)
                        q.foto.save(f"perfil_{q.email}.png", foto_procesada)  # Guarda la imagen
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
                    messages.success(request, "Correo enviado !!")
                    return redirect('login')
                except Exception as error :
                    messages.error(request, f"No se pudo enviar el correo: {error}")
                    return redirect('login')
            except IntegrityError :
                messages.error(request, 'ERROR : El correo ya esta en uso ')
                return redirect('login')
            except Exception as error :
                    messages.error(request, f"ERROR: {error}")
                    return redirect('login')
        else:
            consulta_roles = Usuarios.ROLES
            contexto = {
                'roles' : consulta_roles
            }
            return render (request,'panel/base_panel.html',contexto)

# Recuperacion de clave por token 
def recueperar_password(request):
    verificar = request.session.get('logueado',False)
    if verificar:
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
                    'Registro de Usuario en Educalab',
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

def verificacion_token_recuperar_password(request):
    verificar = request.session.get('logueado',False)
    if verificar:
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
                    return redirect("login")
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

