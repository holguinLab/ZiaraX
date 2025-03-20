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

# Esta funcion solo muestra el index.html cuando se llama 
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

#USUARIOS
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
        ROLES = Usuarios.ROLES
        contexto = {
            'usuarios' : q,
            'roles' :ROLES
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
                # Si el nombre esta vacio se asigna explorador para que en el envio del correo no quede vacio ni en las tablas
                if nombre  == None :
                    nombre = 'Explorador'
                # segun el rol que inicia sesion se muestra un mensaje si es admin , se redirecciona al panel del administrador
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
        #Si el usuario no existe en la base de datos
        except Usuarios.DoesNotExist :
            messages.error(request,'ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        # si el usuario no existe en la base de datos 
        except NameError :
            messages.error(request,'ERROR : No se encontraron cuentas asociadas')
            request.session['logueado'] = None
        # Errores internos
        except Exception as e :
            messages.error(request,f'ERROR :{e}')
            request.session['logueado'] = None
        return redirect('login')
    else:
        # si el usuario ya incio sesion , no podra devolverse a esta vista , debera cerrar sesion 
        verificar = request.session.get('logueado',False)
        if verificar:
            messages.error(request ,'Ya Iniciaste Sesion ')
            return redirect('index')
        return render(request,'panel/login.html')

def logout(request):
    #si no esta logueado mostrar error y redirecciona al login
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'ERROR : Lo Siento Debes Iniciar Sesion Primero')
        return redirect('login')
    #si ya inicio sesion podra destuir la sesion 
    else:
        try:
            del request.session['logueado']
            messages.success(request,'Se Cerro La Sesion Correctamente')
            return redirect('index')
        # mas que todo este error es por si falla la conexion 
        except Exception as e:
            messages.info(request,f'Ocurrio Un Error Inesperado Intente Nuevamente Detalles: {e}')
        return redirect('index')

def register(request):
    # solo el admin puede crear cuentas de admin y de barbero desde el panel de administrador siendo asi , usamos esta misma vista para procesar tanto los registros de los usuarios como los registros de los barberos y los admistradotrs y clientes , evitando usar muchas funciones de registro tambien evitamos crear formularios ya que el formulario de registro casi siempre es un dropdown que solo admite , correo y password si se va registrar desde la vista de login o index ( sin tener una sesion si ya tiene una sesion no podra ir al login ) , si es desde el panel del admin las opciones cambian y ya puede el admin registrar barberos y admin por medio de un campo que le aparece de ROL 
    """ 
    Función para registrar nuevos usuarios (Clientes, Barberos y Administradores).
    
    - Clientes solo pueden registrarse desde el login/index.
    - Solo los administradores pueden crear cuentas de Barberos y Administradores.
    - Se evita el uso de múltiples vistas y formularios innecesarios.
    """
    
    if request.method == 'POST' :
        foto = request.FILES.get('foto') # Estas opcion esta oculta en el html para todos los roles  pero la pongo para que se pueda procesar la foto decir si es se sube o no 
        rol = request.POST.get('rol') # lo mismo pasa con el rol pero esta opcion si la muestro en el Panel del adminstrador , ya que solo el admin puede crear cuentas con rol  Admin y Barbero (Cuentas con rol Cliente no puede creear)
        password= request.POST.get('password') # Se optiene el password del html
        encriptada = hash_password(password) # se encripta la password del html 
        
        # Try para procesar el guardado de usuario en la BD
        try:
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
                new_barber = Barberos(
                    usuario_barbero = q
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
            # Si no es por que el rol es cliente 
            else:
                messages.success(request,"Su cuenta ha sido registrada con exito")
            
            
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
                if rol == 'B'  or rol == 'A':
                    messages.success(request, "Correo enviado !!")
                    return redirect('listar_usuarios')
                else:
                    messages.success(request, "Correo enviado !!")
                    return redirect('login')
            except Exception as error :
                if rol == 'B'  or rol == 'A':
                    messages.error(request, f"No se pudo enviar el correo: {error}")
                    return redirect('listar_usuarios')
                else:
                    messages.error(request, f"No se pudo enviar el correo: {error}")
                    return redirect('login')
        except IntegrityError :
                if rol == 'B'  or rol == 'A':
                    messages.error(request, 'ERROR : El correo ya esta en uso ')
                    return redirect('listar_usuarios')
                else:
                    messages.error(request, 'ERROR : El correo ya esta en uso ')
                    return redirect('login')

        except Exception as error :
            if rol == 'B' or rol == 'A' :
                messages.error(request, f"ERROR: {error}")
                return redirect('listar_usuarios')
            else:
                messages.error(request, f"ERROR: {error}")
                return redirect('login')
    # si por alguna razon se pone la ruta register que es la que esta en url esta protegida para que aparezca el index
    else:
        return render (request,'index.html')

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

