from django.db import models
# Create your models here.

class Usuarios(models.Model):
    email = models.CharField(max_length=100,unique=True,null=False,blank=False)
    password = models.CharField(max_length=128)
    nombre_completo = models.CharField(max_length=254 ,null=True,blank=True)
    telefono = models.CharField(max_length=16 ,null=True,blank=True)
    f_nacimiento = models.DateField( null=True,blank=True)
    foto = models.ImageField(upload_to="fotos/",blank=True,null=True,default='fotos/predeterminado.png')
    username = models.CharField(max_length=10 , blank=True, null=True,default='')
    ROLES = (
        ("A","Admin"),
        ("B","Barbero"),
        ("C","Cliente"),
    )
    tipoUsuario = models.CharField(max_length=2,choices=ROLES,default='C')
    token_recuperar_clave = models.CharField(max_length=6 , default='')


class Administradores(models.Model):
    usuario_admin = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="administradores") 

class Barberos(models.Model):
    usuario_barbero = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="barberos") 
    admin_creador = models.ForeignKey('Usuarios',on_delete=models.SET_NULL,null=True,related_name="barberos_creados") #Django podría lanzar advertencias si tienes múltiples ForeignKeys apuntando a Usuarios. related name ayuda para eso
    horario_trabajo = models.TextField(null=True,blank=True)
    especialidad = models.CharField(max_length=200,null=True,blank=True)

class Clientes(models.Model):
    usuario_cliente = models.ForeignKey('Usuarios',on_delete=models.CASCADE,related_name="clientes") 

