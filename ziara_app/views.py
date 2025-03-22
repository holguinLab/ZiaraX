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

#region CLIENTES




#endregion

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
        barberos = Barberos.objects.all()
        ROLES = Usuarios.ROLES
        contexto = {
            'usuarios' : q,
            'roles' :ROLES,
            'barberos' :barberos
        }
        return render(request,'admin/usuarios/listar_usuarios.html',contexto)

#SERVICIOS
def listar_servicios(request):
    verificar = request.session.get('logueado',False)
    if not verificar :
        messages.info(request,'Debes Iniciar Sesion Primero')
        return redirect('index')
    elif not verificar['rol'] == 'A' :
        messages.warning(request,'No Tienes Permisos Necesarios Para Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        id=request.POST.get('id')
        try:
            servicio = Servicios.objects.get(pk = id)
            servicio.nombre = request.POST.get('nombre')
            servicio.precio = request.POST.get('precio')
            servicio.duracion = request.POST.get('duracion')
            servicio.save()
            messages.success(request,'✅ Servicio Actualizado Correctamente')
            return redirect('listar_servicios')
        except Servicios.DoesNotExist:
            messages.success(request,'❌ No hay Servicios Asociados')
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
        return redirect('listar_servicios')
    else:
        servicios = Servicios.objects.all()
        contexto ={
            'servicios' : servicios
        }
        return render(request,'admin/servicios/listar_servicios.html',contexto)

#AÑADIR SERVICIO
def nuevo_servicio(request):
    verificar = request.session.get('logueado',False)
    if not verificar :
        messages.info(request,'Debes Iniciar Sesion Primero')
        return redirect('index')
    elif not verificar['rol'] == 'A' :
        messages.warning(request,'No Tienes Permisos Necesarios Para Hacer Esto')
        return redirect('index')
    if request.method == 'POST':
        try:
            nuevo = Servicios(
                nombre = request.POST.get('nombre'),
                precio = request.POST.get('precio'),
                duracion = request.POST.get('duracion')
            )
            nuevo.save()
            messages.success(request,' ✅ Servicio Agregado Con Exito')
            return redirect('listar_servicios')
        except Exception as e:
            messages.error(request,f' ❌ ERROR : {e}')
            return redirect('listar_servicios')
    else:
        return redirect('listar_servicios')

#BARBEROS
def detalles_barberos(request,id_barbero):
    verificar = request.session.get('logueado',False)
    if verificar == False :
        messages.warning(request,'ERROR : Debes Iniciar Sesion Primero ')
        return redirect('login')
    elif not verificar['rol'] == 'A':
        messages.warning(request,'ERROR : NO TIENES LOS PERMISOS NECESARIOS 🚫 ')
        return redirect('index')
    else:
        try:
            barbero = Barberos.objects.get(pk = id_barbero)
            contexto = {
                'barbero' : barbero
            }
            return render(request,'admin/usuarios/detalles_barberos.html',contexto)
        except Exception as e:
            messages.error(request,f'ERROR : {e}')
            return redirect('listar_usuarios')

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

#Destruir sesion
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
                    messages.success(request, "Correo enviado !!")
                except Exception as error :
                    messages.error(request, f"No se pudo enviar el correo: {error}")
                return redirect('listar_usuarios')

            except IntegrityError :
                messages.error(request, 'ERROR : El correo ya esta en uso ')
                
            except Exception as error :
                messages.error(request, f"ERROR: {error}")
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
            
            # Try para procesar el guardado de usuario en la BD
            try:
                # Se asigna la variable que guardara el usuario 
                q = Usuarios(
                email = request.POST.get('email'), # se obtine el email del formulario (en este caso esta funcion esta para funcionar atravves de una url asiganada en un action de un html)
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
                """ try:
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
                return redirect('login') """
            
            except IntegrityError :
                messages.error(request, 'ERROR : El correo ya esta en uso ')
            except Exception as error :
                messages.error(request, f"ERROR: {error}")
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
            foto_subida = request.FILES.get('foto')
            if foto_subida:
                #Se hace la foto redonda para evitar que suban fotos de cualquier tamaño
                foto_procesada = hacer_imagen_redonda(foto_subida)
                # Borrar la imagen anterior para evitar archivos basura
                if usuario.foto:
                    usuario.foto.delete(save=False)

                # 🔵 Generar un nombre seguro para el archivo Este paso se puede omitir por nombre_archivo = f"{usuarioLogeado.id}.png" si no queremos usar las librerias
                user_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', usuario.username)  # Limpia caracteres especiales
                nombre_archivo = f"{user_clean}_{uuid.uuid4().hex[:8]}.png"
                usuario.foto.save(nombre_archivo, foto_procesada, save=True) # ! Esto sobrescribe la imagen que ya tiene guardada en media 
            else:
                usuario.save() # * Guarda los cambios en la BD
            del request.session['logueado']
            messages.info(request,'Tu información se ha actualizado. Por favor, inicia sesión nuevamente.')
            return redirect('index')
        except Exception as e:
            messages.error(request,f'{e}')
            return redirect('index')
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

