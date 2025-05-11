from django.db import models
from django.utils.timezone import now
from datetime import time
from django.core.validators import validate_image_file_extension  # Importa el validador

# Create your models here.

class Usuarios(models.Model):
    estado=models.CharField(max_length=15,default='Activo')
    email = models.CharField(max_length=100,unique=True,null=False,blank=False)
    password = models.CharField(max_length=128,blank=False,null=False)
    nombre_completo = models.CharField(max_length=254 ,null=True,blank=True)
    telefono = models.CharField(max_length=16 ,null=True,blank=True)
    f_nacimiento = models.DateField( null=True,blank=True)
    foto = models.ImageField(upload_to="fotos/",blank=True,null=True,default='fotos/predeterminado.png',validators=[validate_image_file_extension])
    username = models.CharField(max_length=10 , blank=True, null=True,default='')
    ROLES = (
        ("A","Admin"), 
        ("B","Barbero"),
        ("C","Cliente"),
    )
    tipoUsuario = models.CharField(max_length=2,choices=ROLES,default='C')
    token_recuperar_clave = models.CharField(max_length=6 , default='')
    
    def __str__(self):
        return f' {self.nombre_completo} - {self.email}'

class Administradores(models.Model):
    usuario_admin = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="administradores") 

class Barberos(models.Model):
    usuario_barbero = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="barberos") 
    admin_creador = models.ForeignKey('Usuarios',on_delete=models.SET_NULL,null=True,related_name="barberos_creados") #Django podría lanzar advertencias si tienes múltiples ForeignKeys apuntando a Usuarios. related name ayuda para eso
    DIAS = (
        ('semana','Lunes a Jueves'),
        ('fin_semana','Viernes a Domingo')
    )
    horario_trabajo = models.CharField(max_length=100,choices=DIAS,default='')
    hora_inicio = models.TimeField(default=time(9, 0))
    hora_final = models.TimeField(default=time(16, 0))
    experiencia = models.IntegerField(null=True,blank=True,default=0)
    especialidad = models.CharField(max_length=200,null=True,blank=True)
    
    def __str__(self):
        return f' {self.usuario_barbero} '

class Clientes(models.Model):
    usuario_cliente = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="clientes") 
    
    def __str__(self):
        return f' {self.usuario_cliente} '

class Servicios(models.Model):
    nombre = models.CharField(max_length=100,null=False,blank=False)
    precio = models.DecimalField(max_digits=12,decimal_places=3,null=False,blank=False)
    duracion = models.CharField(max_length=100,blank=True,null=True ,default='')
    descripcion = models.CharField(max_length=200,blank=True,null=True,default='')
    img_url = models.URLField(blank=True, null=True)  # Guarda la URL completa de la imagen
    CATEGORIAS = (
        ("B","Barba"),
        ("C","Cabello"),
        ("S","Spa"),
    )
    categoria = models.CharField(max_length=1,choices=CATEGORIAS,default='')
    def __str__(self):
        return f' {self.nombre} '

class Citas(models.Model):
    cliente = models.ForeignKey('Clientes',on_delete=models.CASCADE,related_name="cita_cliente") 
    barbero = models.ForeignKey('Barberos',on_delete=models.SET_NULL,null=True,related_name="cita_barbero") 
    fecha = models.DateField(default=now ,null=True,blank=True)
    hora = models.TimeField(default=now)
    ESTADOS =(
        ("PEN","Pendiente"),
        ("PRO","Programada"),
        ("CAN","Cancelada"),
        ("FIN","Finalizada"),
    )
    estado = models.CharField(max_length=3,choices=ESTADOS)
    
    def __str__(self):
        return f' {self.cliente} - {self.barbero} '

class Productos(models.Model):
    nombre = models.CharField(max_length=100,null=False,blank=False)
    precio = models.DecimalField(max_digits=12,decimal_places=3,null=False,blank=False)
    descripcion = models.TextField(blank=True,null=True,default='')
    img_url = models.URLField(blank=True, null=True)  # Guarda la URL completa de la imagen
    CATEGORIAS = (
        ("B","Barba"),
        ("C","Cabello"),
        ("R","Rostro"),
        ("N","Natural"),
        ("P","Cuerpo"),
    )
    categoria = models.CharField(max_length=1,choices=CATEGORIAS,default='')
    def __str__(self):
        return f' {self.nombre} '    

class Inventarios(models.Model):
    producto = models.ForeignKey('Productos',on_delete=models.CASCADE,related_name='inventario_productos')
    stock = models.IntegerField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)    

# Un cliente puede tener muchos servicios
class CitaServicios(models.Model):
    cita = models.ForeignKey('Citas',on_delete=models.CASCADE,related_name="citas")
    servicio = models.ForeignKey('Servicios', on_delete=models.SET_NULL, null=True, blank=True, related_name="cita_servicio")


class Pagos(models.Model):
    cliente = models.ForeignKey('Clientes', on_delete=models.CASCADE, related_name="pagos")
    cita = models.ForeignKey('Citas', on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos_cita")
    fecha_pago = models.DateTimeField(default=now)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)



class ProductosComprados(models.Model):
    pago = models.ForeignKey('Pagos', on_delete=models.CASCADE, related_name='productos_comprados')
    producto = models.ForeignKey('Productos', on_delete=models.CASCADE)